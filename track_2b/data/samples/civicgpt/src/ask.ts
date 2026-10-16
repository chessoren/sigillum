import OpenAI from "openai";

const client = new OpenAI({ apiKey: process.env.OPENAI_KEY });

export async function ask(question: string) {
  const r = await client.chat.completions.create({ model: "gpt-4o", messages: [{ role: "user", content: question }] });
  return r.choices[0].message.content;
}
