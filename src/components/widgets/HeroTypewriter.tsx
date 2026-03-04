import React from 'react';
import { Typewriter } from 'react-simple-typewriter';

export default function TypewriterVersion() {
    return (
        <div className="text-xl md:text-2xl mt-4 font-mono font-medium opacity-80 backdrop-blur-sm bg-white/30 dark:bg-slate-900/40 rounded-lg inline-block px-4 py-2 border border-black/5 dark:border-white/10 shadow-sm">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-emerald-500 dark:from-blue-400 dark:to-emerald-300">
                <Typewriter
                    words={[
                        'Version 2026.03: 正在尝试与焦虑和解',
                        'Version 1.0: 保持好奇心的探索者',
                        'Version 2.0: 坚定的技术实践者',
                        'Version NOW: 享受生活与每一行代码',
                    ]}
                    loop={0} // 0 means infinite loop
                    cursor
                    cursorStyle="_"
                    typeSpeed={80}
                    deleteSpeed={50}
                    delaySpeed={2000}
                />
            </span>
        </div>
    );
}
