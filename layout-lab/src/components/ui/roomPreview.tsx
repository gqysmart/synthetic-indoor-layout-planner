

export function RoomPreview({ width, height }: { width: number, height: number }) {
    return (
        <div className="p-4 border rounded bg-white shadow-sm space-y-4">
            <h2 className="text-lg font-bold">Room Preview</h2>

            <div className="bg-gray-50 p-3 rounded border">
                <h3 className="font-semibold">Room Dimensions</h3>
                <pre className="text-sm">
                    {`Width: ${width}\nHeight: ${height}`}
                </pre>
            </div>
        </div>
    );
}

