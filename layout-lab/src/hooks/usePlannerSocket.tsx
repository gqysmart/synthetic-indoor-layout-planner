// hooks/usePlannerSocket.ts
"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type PlannerStatus = "idle" | "connecting" | "open" | "closed" | "error";

export type RoomLayoutContext = {
    room: string | null;
    furnitures: string[];
    algorithm: string | null;
};

type PlannerMessage = {
    // 根据你后端的返回结构改
    type: string;
    payload?: unknown;
};

export function usePlannerSocket(url_server: string, onMessage?: (msg: PlannerMessage) => void) {
    const wsRef = useRef<WebSocket | null>(null);
    const jobidRef = useRef<string | null>(null);
    const [status, setStatus] = useState<PlannerStatus>("idle");

    const startSocket = useCallback(
        (jobId: string) => {
            // 已经有连接就先关掉

            // const url = `${process.env.NEXT_PUBLIC_PLANNER_WS_URL ?? "ws://localhost:8000"}/ws/planner/${jobId}`;
            if (jobId === jobidRef.current && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                return; // 避免重复连接
            }

            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.close();
            }

            jobidRef.current = jobId;
            const url = `wss://${url_server}/planner/ws/${jobId}`;
            const ws = new WebSocket(url);

            wsRef.current = ws;
            setStatus("connecting");

            ws.onopen = () => {
                setStatus("open");

                // 这里就是你说的 startSocketCommand with context 参数

            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as PlannerMessage;
                    onMessage?.(data);
                } catch (e) {
                    console.warn("planner ws invalid message", event.data);
                }
            };

            ws.onclose = () => {
                setStatus("closed");
            };

            ws.onerror = () => {
                setStatus("error");
            };
        },
        [onMessage, url_server]
    );

    const sendCommand = useCallback((message: PlannerMessage) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            console.warn("planner ws not open, cannot send", message);
            return;
        }
        try {
            ws.send(JSON.stringify(message));
        } catch (e) {
            console.error("planner ws send failed", e);
        }
    }, []);

    const stopSocket = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
            setStatus("closed");
        }
    }, []);

    // 组件卸载时自动断开
    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, []);

    return { status, startSocket, sendCommand, stopSocket };
}
