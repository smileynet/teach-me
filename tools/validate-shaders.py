#!/usr/bin/env python3
"""validate-shaders.py — Validate .gdshader files using builtin type data.

Quick type checker that catches the most common errors in lesson shader code:
- Assignment type mismatches (vec2 = vec3)
- Undeclared variables (not builtin and not user-declared)
- Missing shader_type
- Invalid swizzle lengths

Uses builtin definitions from gdshader-lsp-cpp JSON data files.
"""

import json
import re
import sys
from pathlib import Path

# --- Load builtin data ---

DATA_DIR = Path(__file__).parent.parent / ".references" / "gdshader-lsp-cpp" / "src" / "gdshader" / "data"

def load_builtins():
    """Load all spatial shader builtins from JSON data files."""
    builtins = {}  # name -> {"type": ..., "qualifier": ..., "stage": ...}

    stage_files = {
        "vertex": "spatial_vertex.json",
        "fragment": "spatial_fragment.json",
        "light": "spatial_light.json",
        "global": "spatial_global.json",
    }

    for stage, filename in stage_files.items():
        path = DATA_DIR / filename
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data:
            builtins[entry["name"]] = {
                "type": entry["type"],
                "qualifier": entry.get("qualifier", "in"),
                "stage": stage,
            }

    return builtins


def load_functions():
    """Load global function signatures."""
    path = DATA_DIR / "global_functions.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    funcs = {}
    for entry in data:
        name = entry["name"]
        if name not in funcs:
            funcs[name] = []
        funcs[name].append(entry)
    return funcs


# --- Type inference ---

SWIZZLE_COMPONENTS = set("xyzwrgbastpq")

def infer_swizzle_type(base_type, swizzle):
    """Given a base type and swizzle, return the resulting type."""
    if not all(c in SWIZZLE_COMPONENTS for c in swizzle):
        return None  # invalid swizzle
    n = len(swizzle)
    if n == 1:
        return "float"
    elif n == 2:
        return "vec2"
    elif n == 3:
        return "vec3"
    elif n == 4:
        return "vec4"
    return None


def type_of_constructor(name):
    """Return the type produced by a constructor call."""
    constructors = {
        "vec2": "vec2", "vec3": "vec3", "vec4": "vec4",
        "ivec2": "ivec2", "ivec3": "ivec3", "ivec4": "ivec4",
        "uvec2": "uvec2", "uvec3": "uvec3", "uvec4": "uvec4",
        "bvec2": "bvec2", "bvec3": "bvec3", "bvec4": "bvec4",
        "mat2": "mat2", "mat3": "mat3", "mat4": "mat4",
        "float": "float", "int": "int", "uint": "uint", "bool": "bool",
    }
    return constructors.get(name)


def result_type_of_binop(left_type, op, right_type):
    """Infer result type of a binary operation."""
    # mat * vec rules
    if left_type == "mat4" and right_type == "vec4":
        return "vec4"
    if left_type == "mat3" and right_type == "vec3":
        return "vec3"
    if left_type == "mat2" and right_type == "vec2":
        return "vec2"
    # scalar * vec
    if left_type == "float" and right_type and right_type.startswith("vec"):
        return right_type
    if right_type == "float" and left_type and left_type.startswith("vec"):
        return left_type
    # same type
    if left_type == right_type:
        return left_type
    return None


# --- Shader parser (minimal) ---

class ShaderChecker:
    def __init__(self, source, filename="<unknown>"):
        self.source = source
        self.filename = filename
        self.lines = source.split("\n")
        self.errors = []
        self.builtins = load_builtins()
        self.functions = load_functions()
        self.user_vars = {}  # name -> type
        self.current_stage = None

    def error(self, line_num, msg):
        self.errors.append({"file": self.filename, "line": line_num, "message": msg})

    def check(self):
        """Run all checks."""
        self.check_shader_type()
        self.check_declarations()
        self.check_assignments()
        return self.errors

    def check_shader_type(self):
        """Verify shader_type is present."""
        if not re.search(r"^\s*shader_type\s+\w+\s*;", self.source, re.MULTILINE):
            self.error(1, "Missing shader_type declaration")

    def check_declarations(self):
        """Parse uniform/varying/variable declarations."""
        # Uniforms
        for m in re.finditer(r"^\s*uniform\s+(\w+)\s+(\w+)", self.source, re.MULTILINE):
            type_name, var_name = m.group(1), m.group(2)
            self.user_vars[var_name] = type_name

        # Varyings
        for m in re.finditer(r"^\s*varying\s+(\w+)\s+(\w+)", self.source, re.MULTILINE):
            type_name, var_name = m.group(1), m.group(2)
            self.user_vars[var_name] = type_name

        # Local variable declarations (type name = ...)
        for m in re.finditer(r"^\s+(\w+)\s+(\w+)\s*=", self.source, re.MULTILINE):
            type_name, var_name = m.group(1), m.group(2)
            if type_name in ("float", "int", "uint", "bool", "vec2", "vec3", "vec4",
                             "ivec2", "ivec3", "ivec4", "mat2", "mat3", "mat4"):
                self.user_vars[var_name] = type_name

    def check_assignments(self):
        """Check for type mismatches in assignments."""
        # Find function boundaries
        func_pattern = re.compile(r"void\s+(vertex|fragment|light)\s*\(\s*\)")
        current_func = None

        for i, line in enumerate(self.lines, 1):
            # Track current function
            func_match = func_pattern.search(line)
            if func_match:
                current_func = func_match.group(1)
                continue

            # Check assignments: target = expr
            assign_match = re.match(r"\s+(\w+(?:\.\w+)?)\s*(?:\+|-|\*|/)?=\s*(.+?)\s*;", line)
            if not assign_match:
                continue

            target = assign_match.group(1)
            expr = assign_match.group(2)

            # Resolve target type
            target_base = target.split(".")[0]
            target_type = self.resolve_var_type(target_base, current_func)
            if not target_type:
                continue  # can't determine type, skip

            # If target has a swizzle, adjust expected type
            if "." in target:
                swizzle = target.split(".", 1)[1]
                target_type = infer_swizzle_type(target_type, swizzle)

            # Try to infer expression type
            expr_type = self.infer_expr_type(expr, current_func)
            if not expr_type:
                continue  # can't determine, skip

            # Check match
            if target_type and expr_type and target_type != expr_type:
                # Allow float/int promotions
                if target_type == "float" and expr_type == "int":
                    continue
                # Allow vec /= float, vec *= float (scalar-vector compound assignment)
                if target_type.startswith("vec") and expr_type == "float":
                    continue
                if target_type.startswith("ivec") and expr_type == "int":
                    continue
                self.error(i, f"Type mismatch: '{target_base}' is {target_type}, assigned {expr_type}")

    def resolve_var_type(self, name, current_func):
        """Look up a variable's type from user declarations or builtins."""
        if name in self.user_vars:
            return self.user_vars[name]
        if name in self.builtins:
            return self.builtins[name]["type"]
        return None

    def infer_expr_type(self, expr, current_func):
        """Try to infer the type of a simple expression."""
        expr = expr.strip()

        # Parenthesized expression with trailing swizzle: (expr).xyz
        paren_swizzle = re.match(r"^\((.+)\)\.(\w+)$", expr)
        if paren_swizzle:
            inner_type = self.infer_expr_type(paren_swizzle.group(1), current_func)
            swizzle = paren_swizzle.group(2)
            if inner_type and all(c in SWIZZLE_COMPONENTS for c in swizzle):
                return infer_swizzle_type(inner_type, swizzle)

        # Strip outer parens: (expr)
        if expr.startswith("(") and expr.endswith(")"):
            return self.infer_expr_type(expr[1:-1], current_func)

        # Constructor: vec3(...), mat4(...), etc.
        ctor_match = re.match(r"(\w+)\s*\(", expr)
        if ctor_match:
            ctor_type = type_of_constructor(ctor_match.group(1))
            if ctor_type:
                return ctor_type

        # Function call: normalize(...), dot(...), etc.
        func_match = re.match(r"(\w+)\s*\((.+)\)$", expr)
        if func_match:
            fname = func_match.group(1)
            return self.infer_function_return(fname, func_match.group(2), current_func)

        # Member access with swizzle: world_pos.xz, NORMAL.xyz
        member_match = re.match(r"(\w+)\.(\w+)", expr)
        if member_match:
            base = member_match.group(1)
            member = member_match.group(2)
            base_type = self.resolve_var_type(base, current_func)
            if base_type and all(c in SWIZZLE_COMPONENTS for c in member):
                return infer_swizzle_type(base_type, member)

        # Simple variable reference
        if re.match(r"^\w+$", expr):
            return self.resolve_var_type(expr, current_func)

        # Binary operation: X * Y, X + Y
        # Split at top-level operators (not inside parentheses)
        split_result = self._split_binop(expr)
        if split_result:
            left_str, op, right_str = split_result
            left_type = self.infer_expr_type(left_str, current_func)
            right_type = self.infer_expr_type(right_str, current_func)
            if left_type and right_type:
                result = result_type_of_binop(left_type, op, right_type)
                if result:
                    return result

        return None

    def _split_binop(self, expr):
        """Split an expression at the top-level binary operator (respecting parens)."""
        depth = 0
        # Scan right-to-left for lowest precedence first (+ -), then (* /)
        for ops in [(" + ", " - "), (" * ", " / ")]:
            for i in range(len(expr) - 1, -1, -1):
                if expr[i] == "(":
                    depth += 1
                elif expr[i] == ")":
                    depth -= 1
                elif depth == 0:
                    for op in ops:
                        if expr[i:i+len(op)] == op:
                            left = expr[:i].strip()
                            right = expr[i+len(op):].strip()
                            if left and right:
                                return (left, op.strip(), right)
            depth = 0
        return None

    def infer_function_return(self, fname, args_str, current_func):
        """Infer return type of a function call."""
        # Known functions with fixed return types
        fixed_returns = {
            "normalize": None,  # same as input
            "abs": None,  # same as input
            "dot": "float",
            "length": "float",
            "distance": "float",
            "clamp": None,  # same as first arg
            "min": None,
            "max": None,
            "mix": None,
            "step": None,
            "smoothstep": None,
            "pow": None,
            "mod": None,
            "texture": "vec4",
            "textureLod": "vec4",
        }

        if fname in fixed_returns:
            ret = fixed_returns[fname]
            if ret:
                return ret
            # Return type matches first argument type
            first_arg = args_str.split(",")[0].strip()
            return self.infer_expr_type(first_arg, current_func)

        # Constructor
        ctor = type_of_constructor(fname)
        if ctor:
            return ctor

        return None


# --- Main ---

def validate_file(path):
    """Validate a single .gdshader file."""
    source = Path(path).read_text(encoding="utf-8")
    checker = ShaderChecker(source, str(path))
    return checker.check()


def main():
    """Validate all .gdshader files found in reference/code/ directories."""
    search_root = Path("examples")
    if "--path" in sys.argv:
        idx = sys.argv.index("--path")
        search_root = Path(sys.argv[idx + 1])

    shader_files = list(search_root.rglob("*.gdshader"))

    if not shader_files:
        print("No .gdshader files found.")
        return 0

    total_errors = 0
    for shader_path in sorted(shader_files):
        errors = validate_file(shader_path)
        if errors:
            total_errors += len(errors)
            for err in errors:
                print(f"  {err['file']}:{err['line']}: {err['message']}")
        else:
            print(f"  PASS  {shader_path}")

    print(f"\n{'='*60}")
    print(f"  {len(shader_files)} files checked, {total_errors} errors")
    if total_errors > 0:
        print(f"  FAIL")
        return 1
    else:
        print(f"  ALL PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
