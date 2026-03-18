import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function GET() {
  const res = await fetch(`${API_URL}/sessions`);
  const data = await res.json();
  return NextResponse.json(data);
}
