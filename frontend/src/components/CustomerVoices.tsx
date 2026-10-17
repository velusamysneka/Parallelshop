import type { CustomerVoice } from "../types";
import { personaMeta } from "../format";

export default function CustomerVoices({ voices }: { voices: CustomerVoice[] }) {
  if (!voices.length) return <p className="muted">No agent reasoning returned.</p>;

  return (
    <div className="voices">
      {voices.slice(0, 3).map((v, i) => {
        const meta = personaMeta(v.persona);
        return (
          <blockquote key={i} style={{ borderColor: meta.color }}>
            <p>“{v.quote}”</p>
            <footer>
              <span style={{ color: meta.color }}>{meta.label}</span>
              <span className={`badge ${v.action === "leave" ? "leave" : "buy"}`}>{v.action === "leave" ? "Walked out" : "Bought"}</span>
            </footer>
          </blockquote>
        );
      })}
    </div>
  );
}
