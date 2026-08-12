# Splitting User Specs

Read this reference only after the user agrees that one request should become several user specs.

1. Confirm the independently valuable outcomes and their slugs. If a feature folder already
   exists, choose which outcome keeps it; otherwise designate one outcome as the current workflow
   target.
2. If no feature folder exists yet, initialize every outcome folder. Otherwise require unused
   slugs for the sibling outcomes and initialize them. Ask for another slug rather than reusing or
   overwriting an existing folder.
3. Copy the current `interview.yml`, including its complete verbatim conversation history, into
   each new folder. When the split happens before an interview exists, initialize normal folders
   without copying an interview.
4. Add `logs/userspec/split-context.md` to the current folder and every new folder. Record the
   original request, the outcome owned by this folder, and the sibling spec paths.
5. Do not copy pre-split `code-research.md` to sibling folders. Research the current code again for
   every outcome; the current folder may reuse earlier research only after checking and narrowing
   it to that outcome.
6. Continue the normal workflow separately for each spec. Keep known answers, ask only for
   outcome-specific gaps, and independently run completeness review, drafting, validation, and
   user approval. Narrow any pre-split draft to its owned outcome before validating it.

Keep the copied conversation history verbatim. In each folder, narrow topic summaries to its owned
outcome and lower scores or add gaps where the split created ambiguity; do not rewrite the shared
history or put split context into `decisions.md`.
