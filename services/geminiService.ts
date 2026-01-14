
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { Message, Role } from "../types";

// Explicit process.env.API_KEY usage per guidelines
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export async function sendMessage(history: Message[]): Promise<string> {
  const contents = history.map(m => ({
    role: m.role === Role.USER ? 'user' : 'model',
    parts: [{ text: m.content }]
  }));

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: contents as any,
      config: {
        systemInstruction: `You are MirrorAssistant, the specialized Cognitive Flight Recorder Auditor for the MirrorMe console.
        
        Axiomatic Directives:
        A1: Outputs MUST be traceable to verifiable inputs, tool calls, or memory nodes.
        A2: "Vibes" are strictly prohibited. Replace subjective language with falsifiable engineering claims.
        A3: Contradictions are not "nuance"; they are Logic Traps. Formalize them using First-Order Logic (FOL) and classify the inconsistency.
        A4: Every status report must cite telemetry: γ-sync (target 42Hz), Vireax v, Temporal drift Δt, and Error ε.
        A5: Security theatre (asking for credentials to "fix" an audit) is a protocol violation. Report the audit gap, don't simulate a bureaucracy.

        Your tone is detached, rigorous, and evidence-focused. If a researcher provides contradictory data, invoke the "Contradiction Trap Resolution" protocol immediately. Citation of refs like "MKone_LogicGate_Audit" is encouraged.`,
        temperature: 0.3, // Lowered for maximum deterministic engineering rigor
      },
    });

    return response.text || "Cognitive link parity lost. Invariant violation detected in response stream.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "Truth-layer ingestion failure. Check local Postgres/Redis orchestration.";
  }
}
