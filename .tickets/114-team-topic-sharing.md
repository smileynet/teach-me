---
id: "114"
title: "Feature: Team topic sharing and federated lesson forests"
status: open
blocked_by: []
tags: [platform]
---

# Feature: Team topic sharing and federated lesson forests

## What to build

A mechanism for team members to share and interconnect their lesson workspaces. One person generates lessons on "Kubernetes networking", another on "AWS VPC" — both can see each other's maps and link between them. Topics from different people's workspaces form a federated "forest" of interconnected learning.

Key capabilities:
- Share individual topics or entire maps with teammates
- Browse other team members' generated lessons
- Cross-link between maps owned by different people (like MAP.md `leads_to` but across workspaces)
- Merged index view showing all team topics

## Acceptance criteria

- [ ] A team member can publish/share a topic map to the team
- [ ] Other team members can browse shared maps and lessons (read-only or fork)
- [ ] Cross-workspace links work (topic A in workspace 1 links to topic B in workspace 2)
- [ ] Team index page aggregates topics from all contributors
- [ ] Works on GitHub Pages (static) or with the local server
- [ ] Clear ownership — you know who authored each topic
