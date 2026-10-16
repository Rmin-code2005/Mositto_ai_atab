import React,{useEffect,useRef,useState} from 'react';
export default function Camera({onChange,disabled=false}){
 const video=useRef(null),stream=useRef(null),generation=useRef(0),mounted=useRef(true);
 const [live,setLive]=useState(false),[error,setError]=useState(''),[preview,setPreview]=useState('');
 function stop(){generation.current++;stream.current?.getTracks().forEach(t=>t.stop());stream.current=null;if(video.current)video.current.srcObject=null;setLive(false)}
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;generation.current++;stream.current?.getTracks().forEach(t=>t.stop())}},[]);
 useEffect(()=>()=>{if(preview)URL.revokeObjectURL(preview)},[preview]);
 function select(file){if(!file)return;if(file.size>10*1024*1024){setError('حجم تصویر باید کمتر از ۱۰ مگابایت باشد');return}setError('');setPreview(URL.createObjectURL(file));onChange(file)}
 async function start(){stop();setError('');const token=generation.current;try{
  if(!navigator.mediaDevices?.getUserMedia)throw Error('دوربین فقط روی localhost یا HTTPS در دسترس است');
  const s=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720}},audio:false});
  if(!mounted.current||token!==generation.current){s.getTracks().forEach(t=>t.stop());return}
  stream.current=s;video.current.srcObject=s;await video.current.play();setLive(true);
 }catch(e){if(mounted.current&&token===generation.current){stop();setError(e.name==='NotAllowedError'?'مجوز دوربین رد شد؛ از تنظیمات مرورگر اجازه بدهید':e.name==='NotFoundError'?'دوربینی پیدا نشد':e.message)}}}
 function capture(){const v=video.current;if(!v?.videoWidth)return;const canvas=document.createElement('canvas');canvas.width=v.videoWidth;canvas.height=v.videoHeight;canvas.getContext('2d').drawImage(v,0,0);canvas.toBlob(b=>{if(b&&mounted.current)select(new File([b],'camera.jpg',{type:'image/jpeg'}))},'image/jpeg',.92)}
 return <div className="camera"><div className="viewfinder"><video ref={video} autoPlay muted playsInline hidden={!live}/>{!live&&<div className="placeholder"><span>◎</span><strong>تصویر روشن، شناسایی بهتر</strong><small>چهره را روبه‌روی دوربین قرار دهید</small></div>}{live&&<span className="live">● دوربین روشن</span>}</div><div className="actions"><button type="button" disabled={disabled} onClick={live?stop:start}>{live?'خاموش‌کردن دوربین':'روشن‌کردن دوربین'}</button><button type="button" className="primary" disabled={!live||disabled} onClick={capture}>گرفتن عکس</button><label className="upload">انتخاب فایل<input aria-label="انتخاب عکس" type="file" accept="image/jpeg,image/png,image/webp" disabled={disabled} onChange={e=>{select(e.target.files[0]);e.target.value=''}}/></label></div>{error&&<p role="alert" className="error">{error}</p>}{preview&&<div className="capture"><img src={preview} alt="تصویر آماده ارسال"/><div><strong>تصویر آماده ارسال</strong><p>عکس فقط پس از زدن دکمه ثبت ارسال می‌شود.</p></div></div>}</div>
}
