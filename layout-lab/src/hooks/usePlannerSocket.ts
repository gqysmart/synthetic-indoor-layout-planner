// hooks/usePlannerSocket.ts
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { WsIncomingMessage } from "@/lib/types/websocketMessage";

export type PlannerStatus = "idle" | "connecting" | "open" | "closed" | "error";

export type RoomLayoutContext = {
    room: string | null;
    furnitures: string[];
    algorithm: string | null;
};

export function usePlannerSocket(onMessage?: (msg: WsIncomingMessage) => void) {
    const wsRef = useRef<WebSocket | null>(null);
    const wsUrlRef = useRef<string | null>(null);
    const onMessageRef = useRef<typeof onMessage>(undefined);
    const [status, setStatus] = useState<PlannerStatus>("idle");

    // 始终保持最新的 onMessage
    useEffect(() => {
        onMessageRef.current = onMessage;
    }, [onMessage]);

    const startSocket = useCallback((ws_url: string) => {
        // 避免同一个 URL 重复连接
        if (
            ws_url === wsUrlRef.current &&
            wsRef.current &&
            wsRef.current.readyState === WebSocket.OPEN
        ) {
            return;
        }

        // 如果之前有打开的连接，先关掉
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.close();
        }

        wsUrlRef.current = ws_url;
        console.log("Connecting to planner ws:", ws_url);

        const ws = new WebSocket(ws_url);
        wsRef.current = ws;
        setStatus("connecting");

        ws.onopen = () => {
            setStatus("open");
            // 这里可以在连上以后自动发一条初始化命令，如果你想的话
            // e.g. onMessageRef.current?.({ type: 'connected' } as any)
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data) as WsIncomingMessage;
                // 用最新的 onMessage
                if (onMessageRef.current) {
                    onMessageRef.current(data);
                }
            } catch (e) {
                console.warn("planner ws invalid message", event.data, e);
            }
        };

        ws.onclose = () => {
            setStatus("closed");
        };

        ws.onerror = () => {
            setStatus("error");
        };
    }, []); // ⬅️ 现在没有依赖 onMessage 了，startSocket 是稳定引用

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
    }, []); // 同样是稳定引用

    const stopSocket = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
            setStatus("closed");
        }
    }, []); // 稳定引用

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
