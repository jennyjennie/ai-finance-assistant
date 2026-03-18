import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function GET(
  _: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const res = await fetch(`${API_URL}/sessions/${id}/messages`);
  const data = await res.json();
  return NextResponse.json(data);
}
