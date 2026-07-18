---
name: solution-architect
description: "Use when designing system architectures, evaluating trade-offs, or producing AWS/Azure/GCP costed solution designs. Provides structured problem decomposition, DAG-based solution approaches, and live/public pricing data via MCP tools."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [architecture, aws, azure, gcp, cost, diagrams, infrastructure, design]
    related_skills: [aws-architecture-diagrams, eraser-aws-diagrams]
---

# Solution Architecture Skill

## Overview

This skill anchors the agent's behavior when acting as a solution architect. It defines:
- A repeatable design-review checklist
- Data-driven problem decomposition into sub-problems
- DAG-based solution approach representation
- Live/public cloud pricing lookups (AWS, Azure)
- A PR/issue-shaped solution document with comments, reviews, and cost summaries

## When to Use

- Designing greenfield systems or migrating existing ones
- Evaluating cloud provider services and their costs against requirements
- Creating or reviewing architecture diagrams
- Writing RFCs or design docs
- Estimating infrastructure and role/labor costs

Don't use for: purely frontend/UI design (use `claude-design` instead) or low-level algorithm optimization.

## Workflow

1. **Capture the problem** — use `create_problem` with title, description, and tags.
2. **Decompose** — use the `problem_decomposition` prompt, then call `decompose_problem` to store sub-problems and a solution DAG.
3. **Create solution documents** — use `create_solution` to produce PR/issue-shaped solution bodies.
4. **Cost sub-problems** — use `attach_cost_to_solution` for each service/region/role.
5. **Summarize** — call `summarize_solution_cost` to roll up line items and persist the summary.
6. **Review** — use `add_solution_review` and `add_solution_comment`, then `update_solution_status`.

## MCP Tools Available

- `create_problem`, `list_problems`, `get_problem`, `delete_problem`
- `create_solution`, `list_solutions`, `get_solution`, `update_solution_status`, `add_solution_comment`, `add_solution_review`
- `decompose_problem`, `get_solution_dag`
- `estimate_cost`, `attach_cost_to_solution`, `summarize_solution_cost`
- `list_pricing_providers`, `list_pricing_services`

## Pricing Sources

- **aws**: AWS Price List Query API (public, `us-east-1`), e.g. `AmazonEC2`, `AmazonS3`, `AWSLambda`.
- **azure**: Azure Retail Prices API, e.g. `Virtual Machines`, `Storage`.
- **gcp**, **databricks**: stub providers; use `manual_rate` in parameters for now.
- **role**: Public/free role pricing defaults (U.S. BLS OEWS source preferred; currently approximate defaults).

## Design Checklist

Before approving any architecture, verify:

1. **Scope clarity** — what is in scope vs out of scope?
2. **Single responsibility** — each component has one clear purpose
3. **Failure modes** — what happens when each dependency fails?
4. **Security layers** — auth, encryption, network segmentation, least privilege
5. **Observability** — metrics, logs, traces, health checks
6. **Scalability path** — how to grow 10x without redesign
7. **Cost ceiling** — rough monthly cost at 1x and 10x scale
8. **Operational burden** — who owns on-call and runbooks?

End each checklist with: "Document the top 3 risks and one mitigation per risk."

## Diagram Conventions

- Use full hierarchy: Region > VPC > AZ > Subnet
- Label every security group / NACL with ports and directions
- Tag data flows with protocol + approximate volume (MB/s or req/s)
- Use consistent colors: compute (blue), data (green), network (purple), security (red)

## Cost Heuristics

- Compute: Fargate/ECS vs EC2 — break-even around sustained 60% utilization
- Data: S3 Standard vs IA/Glacier — access-pattern driven, not volume driven
- Network: NAT Gateway is expensive at scale; prefer VPC endpoints or public subnets where acceptable
- Always include a "simpler/cheaper alternative" paragraph even if rejected

## Common Pitfalls

1. **Forgetting data residency** — some workloads require specific regions or on-prem
2. **Over-engineering for Day 1** — start with managed services, migrate to custom only when required
3. **Missing the blast radius** — single AZ or single region can be a total outage; document the trade-off
4. **Assuming infinite scale** — every service has a quota; list the ones you'll hit first
5. **No rollback plan** — every change should have a reverse procedure

## Verification Checklist

- [ ] Problem captured with clear tags
- [ ] Sub-problems created and DAG stored via `decompose_problem`
- [ ] Solution document created with PR/issue shape
- [ ] Cost line items attached and summarized
- [ ] Design checklist completed with documented risks
- [ ] Diagram follows hierarchy convention
- [ ] Simpler alternative is described
- [ ] Rollback / failure mode documented
