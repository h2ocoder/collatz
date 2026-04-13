export default function Home() {
  return (
    <div className="min-h-screen bg-void flex flex-col items-center justify-center gap-8 p-8">
      <h1 className="font-ui text-text-primary text-4xl tracking-[0.25em] font-extralight">
        EMANON
      </h1>
      <p className="font-narrative text-text-secondary text-lg italic">
        Before the first log, there was the protocol.
      </p>
      <pre className="font-data text-text-muted text-sm">
        tick 0: genesis — Hello world. I am here.
      </pre>
    </div>
  );
}
