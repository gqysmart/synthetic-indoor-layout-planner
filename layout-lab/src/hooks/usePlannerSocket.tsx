// hooks/usePlannerSocket.ts
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getPlannerWsUrl } from "@/lib/wbsocket/url";
import { get } from "http";

export type PlannerStatus = "idle" | "connecting" | "open" | "closed" | "error";

export type RoomLayoutContext = {
    room: string | null;
    furnitures: string[];
    algorithm: string | null;
};

// type PlannerMessage = {
//     // 根据你后端的返回结构改
//     type: string;
//     payload?: unknown;
// };
import { WsIncomingMessage } from "@/lib/types/websocketMessage";

export function usePlannerSocket(onMessage?: (msg: WsIncomingMessage) => void) {
    const wsRef = useRef<WebSocket | null>(null);
    const wsUrlRef = useRef<string | null>(null);
    const [status, setStatus] = useState<PlannerStatus>("idle");

    const startSocket = useCallback(
        (ws_url: string) => {
            // 已经有连接就先关掉


            // const url = `${process.env.NEXT_PUBLIC_PLANNER_WS_URL ?? "ws://localhost:8000"}/ws/planner/${jobId}`;
            if (ws_url === wsUrlRef.current && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                return; // 避免重复连接
            }

            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.close();
            }

            wsUrlRef.current = ws_url;
            const ws = new WebSocket(ws_url);

            wsRef.current = ws;
            setStatus("connecting");

            ws.onopen = () => {
                setStatus("open");

                // 这里就是你说的 startSocketCommand with context 参数

            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as WsIncomingMessage;
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
        []
    );

    const sendCommand = useCallback((message: WsIncomingMessage) => {
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
