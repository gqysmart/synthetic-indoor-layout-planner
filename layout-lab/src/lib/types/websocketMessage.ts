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


  export type WsCommandMessage = WsMessageBase<
  "command",
  {
    command:string;
    room?: string |null;
    furnitures?: string[] |null;
    algorithm?: string | null;
  }
>;
export type WsIncomingMessage =
  | WsStatusMessage
  | WsCommandMessage
  | WsErrorMessage
  | WsPathResponseMessage;
