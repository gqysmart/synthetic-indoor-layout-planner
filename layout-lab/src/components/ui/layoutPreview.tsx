// components/LayoutPreview.tsx
"use client";

import React from "react";
import type { LayoutDTO } from "@/lib/types/websocketMessage";
import { FurniturePreview } from "./furniturePreview";
import { RoomPreview } from "./roomPreview";

interface Props {
    layout: LayoutDTO | null;
}

export function LayoutPreview({ layout }: Props) {
    if (!layout) {
        return (
            <div className="p-4 border rounded bg-gray-50 text-gray-500">
                No layout loaded.
            </div>
        );
    }

    return (
        <div className="p-4 border rounded bg-white shadow-sm space-y-4">
            <h2 className="text-lg font-bold">{layout.name}</h2>

            <div className="bg-gray-50 p-3 rounded border">
                <h3 className="font-semibold">Room</h3>
                <RoomPreview width={layout.room.width} height={layout.room.height} />
            </div>

            <div className="bg-gray-50 p-3 rounded border">
                <h3 className="font-semibold">Furnitures ({layout.furnitures.length})</h3>
                {layout.furnitures.map((furniture) => (
                    <FurniturePreview
                        key={furniture.type}
                        width={furniture.width}
                        height={furniture.height}
                        pos_x={furniture.position[0]}
                        pos_y={furniture.position[1]}
                        theta={furniture.rotation} // Assuming theta is not provided in the current data structure
                    />
                ))}
            </div>
        </div>
    );
}
