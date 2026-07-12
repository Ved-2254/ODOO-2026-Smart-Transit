import logoAsset from "@/assets/logo.png";

export function Logo({
  className = "",
  size = 40,
  showWordmark = false,
}: {
  className?: string;
  size?: number;
  showWordmark?: boolean;
}) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <img
        src={logoAsset}
        alt="TransitOps logo"
        width={size}
        height={size}
        style={{ width: size, height: size, objectFit: "contain" }}
        className="block"
      />
      {showWordmark && (
        <span className="font-display text-[22px] font-black tracking-tighter">TransitOps</span>
      )}
    </span>
  );
}
