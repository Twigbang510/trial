declare module 'howler' {
  export class Howl {
    constructor(options: any);
    play(): number;
    pause(): void;
    stop(): void;
    volume(vol?: number): number | void;
    duration(): number;
    seek(seek?: number): number | void;
    playing(): boolean;
    on(event: string, listener: (...args: any[]) => void): void;
    once(event: string, listener: (...args: any[]) => void): void;
  }
  
  export const Howler: {
    autoUnlock: boolean;
    volume(vol?: number): number | void;
    mute(muted?: boolean): boolean | void;
  };
} 