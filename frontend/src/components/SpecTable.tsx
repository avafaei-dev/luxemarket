interface Spec {
    label: string;
    value: string | null | undefined;
  }
  
  interface Props {
    specs: Spec[];
  }
  
  export function SpecTable({ specs }: Props) {
    const filtered = specs.filter((s) => s.value);
  
    return (
      <div className="divide-y divide-gray-800">
        {filtered.map((spec) => (
          <div key={spec.label} className="flex justify-between py-3">
            <span className="text-sm text-gray-500">{spec.label}</span>
            <span className="text-sm text-white font-medium">{spec.value}</span>
          </div>
        ))}
      </div>
    );
  }