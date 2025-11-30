export function getPlannerWsUrl(server: string, jobId: string) {
    const base = server
        .replace(/^http:\/\//, "ws://")
        .replace(/^https:\/\//, "wss://")
        .replace(/\/$/, "");   // 去掉末尾"/"

    return `${base}/plan/ws/jobs/${jobId}`;
}

export function getWSHost():string {
    const host =  "http://localhost:8000";
   // const host = PLANNER_HTTP_BASE
    return host.replace(/\/$/, "");   // 去掉末尾"/"
}
