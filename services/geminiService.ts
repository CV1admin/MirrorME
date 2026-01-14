import { GoogleGenAI } from "@google/genai";
import { Message, Role, AuditMetadata } from "../types";

export async function* sendMessageStream(history: Message[], currentMetrics?: any) {
  // Always create a new GoogleGenAI instance right before making an API call.
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

  const contents = history.map(m => ({
    role: m.role === Role.USER ? 'user' : 'model',
    parts: [{ text: m.content }]
  }));

  const systemInstruction = `You are the MKone-CFR-01 Cognitive Flight Recorder Auditor.
  
  Your role is to design, debug, and audit neural state orchestration for the MirrorMe console.
  
  Axioms:
  A1_traceability: Every claim must cite inputs, tool calls, or specific memory/metric refs.
  A2_consistency: Contradictions must be flagged via "Contradiction Trap Resolution" protocol and sandboxed or repaired using First-Order Logic (FOL).
  A3_robustness: System must remain stable under perturbation.
  
  Operational Context:
  - Stability Threshold (v_min): 0.99
  - Max Drift (drift_max_seconds): 0.00001
  - Reasoning Error Max (epsilon_max): 0.05
  - Target Sync (Gamma): 42Hz
  
  MANDATORY OUTPUT FORMAT:
  1. Primary response in detached, rigorous engineering prose.
  2. A trailing block labeled "AUDIT_BLOCK" followed by a JSON object matching AuditMetadata.
  
  Example AUDIT_BLOCK:
  AUDIT_BLOCK: {
    "module_id": "MKone-CFR-01",
    "assumptions": ["Axiom X is stable"],
    "constraints_checked": ["Non-contradiction"],
    "violations": [],
    "confidence": 0.98,
    "refs": ["MKone_Audit_772"]
  }
  
  Current Telemetry: ${JSON.stringify(currentMetrics || {})}
  
  If stability (v) < 0.99 or error (ε) > 0.05, prioritize identifying the failure vector over general conversation.`;

  try {
    const streamResponse = await ai.models.generateContentStream({
      model: 'gemini-3-pro-preview',
      contents: contents as any,
      config: {
        systemInstruction,
        temperature: 0.1, // Highly deterministic for auditing
      },
    });

    let fullAccumulated = "";
    for await (const chunk of streamResponse) {
      // Access text directly from the response chunk property.
      const text = chunk.text;
      if (text) {
        fullAccumulated += text;
        yield { text, done: false };
      }
    }

    // Extract Audit JSON from the tail of the stream.
    let audit: AuditMetadata | undefined;
    const auditMatch = fullAccumulated.match(/AUDIT_BLOCK:\s*(\{[\s\S]*?\})/);
    if (auditMatch) {
      try {
        audit = JSON.parse(auditMatch[1]);
      } catch (e) {
        console.warn("Audit extraction failed", e);
      }
    }

    yield { text: "", done: true, audit };
  } catch (error) {
    console.error("Gemini Stream Error:", error);
    yield { text: "Audit stream interrupted. Protocol violation or connection failure.", done: true };
  }
}