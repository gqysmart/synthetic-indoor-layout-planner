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

export type WsIncomingMessage =
  | WsStatusMessage
  | WsErrorMessage
  | WsPathResponseMessage;
