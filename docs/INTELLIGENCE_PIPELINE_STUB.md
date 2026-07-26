# MirrorME — intelligence pipeline hard-rule stubs

Client-side enforcers live in `lib/intelligencePipeline/`.

They mirror `Civilisation-one/Router` (`intelligence_router`) and the org contracts under
`Civilisation-one/.github/contracts` (copied to `lib/intelligencePipeline/contracts/`).

## Usage

```ts
import { runScientificPipeline, type RouterRequest, type RouterSession } from '@/lib/intelligencePipeline';

const result = runScientificPipeline({ request, session });
// result.stage === 'awaiting_mk_review' | 'complete' | 'hard_rule_N'
```

## Local bridge

Python bridge module: `local_bridge/intelligence_pipeline/`  
Endpoint (when wired): scientific jobs must pass enforcers before any private engine call.

## Honesty

These are **stubs**. They enforce fail-closed structure and hard rules; they do not
implement production cryptography, identity, or real MKone science.
