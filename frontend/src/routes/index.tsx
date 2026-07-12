import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useDB } from "@/lib/store";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  const session = useDB((d) => d.session);
  const navigate = useNavigate();
  useEffect(() => {
    navigate({ to: session ? "/dashboard" : "/login", replace: true });
  }, [session, navigate]);
  return (
    <div className="min-h-screen bg-[#050811] flex flex-col items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[40%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] bg-primary/10 rounded-full blur-[80px]" />
      </div>
      
      <div className="relative z-10 flex flex-col items-center gap-6">
        <div className="relative flex items-center justify-center w-20 h-20">
          <div className="absolute inset-0 rounded-xl border border-primary/30 animate-ping opacity-25" />
          <div className="absolute inset-0 rounded-xl border-2 border-t-primary border-r-transparent border-b-primary/20 border-l-transparent animate-spin duration-[1200ms]" />
          <div className="w-14 h-14 rounded-lg bg-surface flex items-center justify-center shadow-lg border border-outline-variant">
            <span className="material-symbols-outlined text-primary text-3xl">local_shipping</span>
          </div>
        </div>

        <div className="flex flex-col items-center text-center">
          <h2 className="font-display text-xl font-bold tracking-tight text-white">TransitOps</h2>
          <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-mono mt-1.5 animate-pulse">
            Loading System Core...
          </p>
        </div>
      </div>
    </div>
  );
}
