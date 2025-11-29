export function getPlannerWsUrl(server: string, jobId: string) {
    const base = server
        .replace(/^http:\/\//, "ws://")
        .replace(/^https:\/\//, "wss://")
        .replace(/\/$/, "");   // 去掉末尾"/"

    return `${base}/plan/ws/jobs/${jobId}`;
}

export function getWSHost():string {
    const PLANNER_HTTP_BASE =
        process.env.NEXT_PUBLIC_PLANNER_HTTP_BASE
         ?? "https://synthetic-indoor-layout-planner.onrender.com";
    const host =  "http://localhost:8000";
   // const host = PLANNER_HTTP_BASE
    return host.replace(/\/$/, "");   // 去掉末尾"/"
}