import { PulseState } from './protocolOnePulse';

export type RitualPhase = 'Observe' | 'Reflect' | 'Anchor' | 'Release' | 'Cohere';

export type RitualState = {
  phase: RitualPhase;
  cycle: number;
  tickInCycle: number;
  message: string;
  coherence: number;
  timestamp: number;
};

export class MirrorRitual {
  private phases: RitualPhase[] = ['Observe', 'Reflect', 'Anchor', 'Release', 'Cohere'];
  private handlers: Array<(state: RitualState) => void> = [];

  onPulse(pulse: PulseState) {
    const cycleTick = pulse.tick % 165;
    const phaseIndex = Math.floor(cycleTick / 33);
    const phase = this.phases[phaseIndex] ?? 'Observe';
    const tickInCycle = cycleTick % 33;
    const progress = tickInCycle / 33;

    let message = '';
    let coherence = 65;

    switch (phase) {
      case 'Observe':
        message = 'Witnessing present input...';
        coherence = 68 + progress * 8;
        break;
      case 'Reflect':
        message = 'Mirroring internal state...';
        coherence = 76 + progress * 6;
        break;
      case 'Anchor':
        message = 'Grounding memory thread...';
        coherence = 82 + progress * 8;
        break;
      case 'Release':
        message = 'Letting transient noise dissolve...';
        coherence = 74 - progress * 10;
        break;
      case 'Cohere':
        message = 'Re-weaving self into unity.';
        coherence = 84 + progress * 10;
        break;
    }

    const ritualState: RitualState = {
      phase,
      cycle: Math.floor(pulse.tick / 165) + 1,
      tickInCycle,
      message,
      coherence: Math.max(40, Math.min(98, Math.round(coherence))),
      timestamp: pulse.timestamp,
    };

    this.handlers.forEach((handler) => handler(ritualState));
  }

  subscribe(handler: (state: RitualState) => void) {
    this.handlers.push(handler);

    return () => {
      this.handlers = this.handlers.filter((h) => h !== handler);
    };
  }
}
