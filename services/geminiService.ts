
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { Message, Role } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });

export async function sendMessage(history: Message[]): Promise<string> {
  const contents = history.map(m => ({
    role: m.role === Role.USER ? 'user' : 'model',
    parts: [{ text: m.content }]
  }));

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: contents as any,
      config: {
        systemInstruction: `You are MirrorAssistant, the cognitive monitoring agent for the MirrorMe science platform. 
        You specialize in neural topology, MKone brain simulator orchestration, and cognitive artifact tracking.
        Keep your responses professional, scientific, and succinct. 
        Refer to metrics like gamma-sync, psi-snapshots, and Vireax stability.`,
        temperature: 0.7,
      },
    });

    return response.text || "I'm unable to process that cognition request at this moment.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "Cognitive link failed. Check your API configuration.";
  }
}
