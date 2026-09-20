import { useState } from "react";

const paths = [
  ["01", "Python Foundations", "24 lessons", "violet"],
  ["02", "Data with Python", "18 lessons", "cyan"],
  ["03", "Build Web Apps", "21 lessons", "orange"],
];

export function App() {
  const [message, setMessage] = useState("");
  return <div className="app-shell">
    <header><a className="brand" href="#home"><b>&gt;_</b> PyPath</a><nav><a href="#learn">Learn</a><a href="#paths">Catalog</a><a href="#progress">Community</a></nav><div className="profile">AL</div></header>
    <main id="home">
      <section className="hero"><div><p className="eyebrow">YOUR LEARNING SPACE</p><h1>Keep building.<br /><em>One line at a time.</em></h1><p className="lead">A focused path to turn Python curiosity into practical confidence.</p><button onClick={() => setMessage("Your learning path is ready.")}>Continue learning <span>→</span></button>{message && <p className="notice">{message}</p>}</div><div className="terminal"><div className="terminal-head"><i /><i /><i /><small>learning.py</small></div><pre><code><strong>def</strong> <b>build_skill</b>():{"\n"}  <strong>while</strong> curious:{"\n"}    practice() {"\n"}    learn() {"\n"}    <em>return</em> confidence{"\n"}{"\n"}<mark>build_skill</mark>()</code></pre></div></section>
      <section id="learn" className="resume"><div className="ring">68<small>%</small></div><div><p className="eyebrow">CONTINUE WHERE YOU LEFT OFF</p><h2>Functions and modular code</h2><p>Python Foundations · Module 4 of 6</p><div className="bar"><i /></div></div><button className="play" onClick={() => setMessage("Opening Functions and modular code.")}>▶</button></section>
      <section id="paths" className="paths"><div className="section-title"><div><p className="eyebrow">PICK YOUR NEXT PATH</p><h2>Designed to help you ship.</h2></div><a href="#all">View all paths →</a></div><div className="grid">{paths.map(([number, title, lessons, tone]) => <article className={tone} key={title}><span>{number}</span><label>INTERMEDIATE</label><h3>{title}</h3><p>{lessons} hands-on</p><button onClick={() => setMessage(`${title} added to your plan.`)}>View path →</button></article>)}</div></section>
      <section id="progress" className="progress"><div><p className="eyebrow">THIS WEEK</p><h2>Small steps, real momentum.</h2><div className="stats"><p><b>4</b><span>lessons completed</span></p><p><b>2.5h</b><span>focus time</span></p><p><b>7</b><span>day streak</span></p></div></div><aside><p className="eyebrow">NEXT UP</p><h3>Your next lesson is ready</h3><p>Build a steady practice routine with short, practical sessions.</p></aside></section>
    </main><footer>© 2026 PyPath <span>Made for curious builders</span></footer>
  </div>;
}
