const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{
 const mode=process.argv[2]||'stills';
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'}).catch(()=>chromium.launch());
 const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+__dirname+'/video.html');await p.evaluate(()=>document.fonts.ready);
 if(mode==='stills'){for(const t of [1.8,4.6,6.5,8.2,10.0,12.0,13.8,15.0,17.5,20.6,22.5,25,28]){await p.evaluate(t=>render(t),t);await p.screenshot({path:`still_${t}.png`})}}
 else{const fps=30,dur=30;const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','silent.mp4'],{stdio:['pipe','ignore','inherit']});
  for(let f=0;f<fps*dur;f++){await p.evaluate(t=>render(t),f/fps);const buf=await p.screenshot({type:'jpeg',quality:93});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r))}
  ff.stdin.end();await new Promise(r=>ff.on('close',r))}
 await b.close()})();
