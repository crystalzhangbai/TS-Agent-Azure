---
name: vm-resource-identification
description: "Resolve VM identity/resource info from one of: resource ID, vm name + subscription ID, or private IP (+ optional subscription ID). Use when user gives mixed entry points and you need a canonical VM resource identity before metrics/Kusto investigation."
---

# VM Resource Identification Skill

Use this skill at the beginning of an investigation to normalize user input into a canonical VM identity.

## When To Use

- User gives only private IP.
- User gives vm name + subscription ID.
- User gives full VM resource ID.
- You need a deterministic `subscription_id`, `resource_group`, `vm_name`, `resource_id` for downstream queries.

## Preferred Tool

Call `resolve_vm_resource_info` first.

Supported input patterns:

1. `resource_id` (highest priority)
2. `vm_name + subscription_id`
3. `private_ip + subscription_id`
4. `private_ip` (cross-visible subscriptions)

## Output Contract

Expect normalized fields:

- `subscription_id`
- `resource_group`
- `vm_name`
- `resource_id`
- `private_ip` (if known)
- `vm_size` (if available)
- `match_mode`

## Notes

- If multiple matches are returned, ask user to confirm the target VM before continuing.
- If only private IP is provided and no subscription is provided, search may span all subscriptions visible to current credential.
- If downstream task is platform RCA, pass normalized identity into Kusto investigation flow.
