---
name: solution-architect
description: "Use when designing system architectures, evaluating trade-offs, or producing AWS/Azure/GCP diagrams. Provides structured checklists, diagram conventions, and cost-aware decision guidance."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [architecture, aws, diagrams, infrastructure, design]
    related_skills: [aws-architecture-diagrams, eraser-aws-diagrams]
---

# Solution Architecture Skill

## Overview

This skill anchors the agent's behavior when acting as a solution architect. It defines:
- A repeatable design-review checklist
- Diagram hierarchy conventions (Region → VPC → AZ → Subnet)
- Cost-awareness heuristics
- Decision documentation requirements

## When to Use

- Designing greenfield systems or migrating existing ones
- Evaluating cloud provider services against requirements
- Creating or reviewing architecture diagrams
- Writing RFCs or design docs
- Estimating infrastructure costs

Don't use for: purely frontend/UI design (use `claude-design` instead) or low-level algorithm optimization.

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

- [ ] Design checklist completed with documented risks
- [ ] Diagram follows hierarchy convention and is exported to a file
- [ ] Cost estimate includes 1x and 10x scale
- [ ] Simpler alternative is described
- [ ] Rollback / failure mode documented
