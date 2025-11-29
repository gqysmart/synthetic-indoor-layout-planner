// src/app/api/plan/jobs/route.ts
import { NextResponse } from "next/server";
import { getWSHost ,getPlannerWsUrl} from "@/lib/wbsocket/url";


export async function POST() {
  try {
    const upstream = await fetch(`${getWSHost()}/plan/jobs`, {
      method: "POST",
      // 如果将来你要传 body，可以在这里加 body 和 headers
      // body: await request.text(),
      // headers: { "Content-Type": "application/json" },
    });

    const data = await upstream.json();
    const jobInfo = {server_url: getPlannerWsUrl(getWSHost(), data.job_id)};
    console.log("Created new planner job:", jobInfo);

    return NextResponse.json(jobInfo, { status: upstream.status });
  } catch (err) {
    console.error("Error calling planner /plan/jobs:", err);
    return NextResponse.json(
      { error: "Failed to create job" },
      { status: 500 }
    );
  }
}
