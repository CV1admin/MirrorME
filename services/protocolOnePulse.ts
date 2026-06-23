export type PulseState = {
  tick: number;
  hz: number;
  periodMs: number;
  timestamp: number;
  driftMs: number;
  stable: boolean;
};

export type PulseHandler = (state: PulseState) => void;

export class ProtocolOnePulse {
  private hz: number;
  private periodMs: number;
  private timer: ReturnType<typeof window.setTimeout> | null = null;
  private tick = 0;
  private expected = 0;
  private running = false;
  private handler: PulseHandler;

  constructor(handler: PulseHandler, hz = 33) {
    this.hz = hz;
    this.periodMs = 1000 / hz;
    this.handler = handler;
  }

  start() {
    if (this.running) return;

    this.running = true;
    this.tick = 0;
    this.expected = performance.now() + this.periodMs;

    const step = () => {
      if (!this.running) return;

      const now = performance.now();
      const driftMs = now - this.expected;

      this.tick += 1;

      this.handler({
        tick: this.tick,
        hz: this.hz,
        periodMs: this.periodMs,
        timestamp: now,
        driftMs,
        stable: Math.abs(driftMs) < 5,
      });

      this.expected += this.periodMs;
      const nextDelay = Math.max(0, this.periodMs - driftMs);
      this.timer = window.setTimeout(step, nextDelay);
    };

    this.timer = window.setTimeout(step, this.periodMs);
  }

  stop() {
    this.running = false;

    if (this.timer !== null) {
      window.clearTimeout(this.timer);
      this.timer = null;
    }
  }

  reset() {
    this.tick = 0;
    this.expected = performance.now() + this.periodMs;
  }
}
