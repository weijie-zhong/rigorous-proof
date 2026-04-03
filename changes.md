I want to the make the following changes to the skill.

# 1. Modes
Simplify the mode choices:
1. Default mode (default terminal mode + auto detect difficulty, with option to force max effort) 
2. Light mode (inline, with option to skip decomposition)

Terminal node: add support for apple & linux

# 2. Iteration logic
When a lemma has fully passed the audit, mark it as pass, no need to audit it in future iterations.

# 3. Fork logic
Add logging so that if a lemma failed 3 times, the default option (when user does not respond) is to accept stronger assumption.