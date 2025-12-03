import { rotate } from "three/tsl"


export function FurniturePreview({ width, height, pos_x, pos_y, theta }:
    { width: number, height: number, pos_x: number, pos_y: number, theta: number }) {


    return (<div className="p-4 border rounded bg-white shadow-sm space-y-4">
        <h2 className="text-lg font-bold">Furniture Preview</h2>

        <div className="bg-gray-50 p-3 rounded border">
            <h3 className="font-semibold">Dimensions</h3>
            <pre className="text-sm">
                Width: {width} units{"\n"}
                Height: {height} units
            </pre>
        </div>

        <div className="bg-gray-50 p-3 rounded border">
            <h3 className="font-semibold">Position</h3>
            <pre className="text-sm">
                X: {pos_x} units{"\n"}
                Y: {pos_y} units
            </pre>
        </div>

        <div className="bg-gray-50 p-3 rounded border">
            <h3 className="font-semibold">Orientation</h3>
            <pre className="text-sm">
                Theta: {theta} degrees
            </pre>
        </div>
    </div>
    );



}