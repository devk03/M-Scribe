// types.ts

export type Timestamp = {
    time: string;
    title: string;
    summary: string;
    emoji: string;
  };
  
  export type TimestampsResponse = {
    timestamps: Timestamp[];
  };