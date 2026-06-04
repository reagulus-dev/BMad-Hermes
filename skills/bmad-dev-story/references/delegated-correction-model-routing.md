# Delegated BMad correction model-routing note

Use this when the user asks Alice/controller to delegate a `bmad-dev-story` correction to a specific model/provider (for example Kimi K2.6, MiniMax, or a local model).

## Durable lesson

`delegate_task` may not expose or honor a per-call model/provider override in the current tool surface. A prompt line such as “run as Kimi K2.6” is only an instruction to the subagent, not a verified routing control. The returned delegate result may report a different actual model.

## Required controller behavior

1. Before delegating, inspect the available delegation interface mentally from the active tool schema:
   - If no per-call model/provider override exists, do **not** imply the requested model is guaranteed.
   - If exact model routing is mandatory, use an available mechanism that actually pins the model (for example a spawned Hermes CLI process with provider/model flags, a profile configured for that model, or a cron/model field when applicable) rather than `delegate_task`.
2. If using `delegate_task` anyway:
   - Put the requested model in the brief as a preference/context only.
   - After it returns, check the returned `model` field if present.
   - Report the actual model honestly when it differs from the requested model.
3. Do not treat “I asked the subagent to use model X” as evidence that model X actually ran.

## BMad-specific guidance

For tiny `bmad-dev-story` corrections, it is acceptable to use the available delegate route if the user’s main intent is delegation and the controller verifies the result. But if the user’s explicit requirement is “must run on Kimi K2.6,” choose a model-pinning execution path or ask for confirmation before proceeding with a non-pinned delegate.
