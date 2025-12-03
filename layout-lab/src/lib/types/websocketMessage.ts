export interface WsMessageBase<Type extends string, Payload> {
  type: Type;
  payload: Payload;
}

export type WsStatusMessage = WsMessageBase<"status", { message: string }>;

export type WsErrorMessage = WsMessageBase<"error", { message: string }>;

export type WsPathResponseMessage = WsMessageBase<
  "path_response",
  {
    command: string;
    path: [number, number][] | null;
  }
>;
export type WsLayoutResponseMessage = WsMessageBase<
  "layout_response",
  {
    command: string;
    layout: LayoutDTO[];
  }
>;
export interface LayoutDTO {
  name:string;
  room: {
    width: number
    height: number
  }
  furnitures: {
    type: string
    width: number
    height: number
    position:[number, number]
    rotation:number
  }[]
}


  export type WsCommandMessage = WsMessageBase<
  "command",

  {
    command:string;
    parameters?: unknown
  
  }
>;
export type WsIncomingMessage =
  | WsStatusMessage
  | WsCommandMessage
  | WsErrorMessage
  | WsPathResponseMessage
  | WsLayoutResponseMessage;
