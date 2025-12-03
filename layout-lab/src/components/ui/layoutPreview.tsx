// components/LayoutPreview.tsx
"use client";

import React from "react";
import type { LayoutDTO } from "@/lib/types/websocketMessage";
import { FurniturePreview } from "./furniturePreview";
import { RoomPreview } from "./roomPreview";

interface Props {
    layout: LayoutDTO | null;
}

// LayoutPreview.tsx

import { LayoutDTO } from "@/lib/types/websocketMessage"

export function LayoutPreview({ layout }: { layout: LayoutDTO | null }) {
    if (!layout) {
        return (
            <div className="p-3 text-xs text-slate-400 flex flex-col items-center justify-center min-h-[96px]">
                <p className="mb-1">No layout selected</p>
                <p className="text-[11px] text-slate-500">
                    Click <span className="font-medium">“Refresh layouts”</span> to load examples.
                </p>
            </div>
        )
    }

    const { room, furnitures } = layout

    return (
        <div className="p-3 text-xs bg-slate-950/60">
            <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-slate-100 truncate">
                    {layout.name ?? "Unnamed layout"}
                </div>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                    {furnitures.length} items
                </span>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-2 text-[11px]">
                <div>
                    <span className="text-slate-400">Width</span>
                    <div className="text-slate-100">
                        {room.width.toFixed(2)} m
                    </div>
                </div>
                <div>
                    <span className="text-slate-400">Height</span>
                    <div className="text-slate-100">
                        {room.height.toFixed(2)} m
                    </div>
                </div>
            </div>

            <div className="border-t border-slate-800 pt-2 mt-1 max-h-20 overflow-y-auto">
                {furnitures.slice(0, 5).map((f, idx) => (
                    <div key={idx} className="flex items-center justify-between mb-1">
                        <span className="text-slate-200 truncate">{f.type}</span>
                        <span className="text-[11px] text-slate-500">
                            ({f.position[0].toFixed(2)}, {f.position[1].toFixed(2)})
                        </span>
                    </div>
                ))}
                {furnitures.length > 5 && (
                    <div className="text-[11px] text-slate-500 mt-1">
                        + {furnitures.length - 5} more…
                    </div>
                )}
            </div>
        </div>
    )
}
