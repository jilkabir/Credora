#!/usr/bin/env python3
"""Credora plug-and-play command line entrypoint."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from scripts.context_bundle import build
from scripts.guided_onboarding import apply_answers, interactive_answers
from scripts.init_user import init_user
from scripts.profile_intelligence import save_for_user
from scripts.review_draft import review
from scripts.social_manager import create_calendar, manager_status, queue_draft, set_approval
from scripts.usability import doctor
from scripts.workspace import user_root
REQUIRED_PROFILE_FILES=["identity.md","positioning.md","expertise.md","audience.md","voice.md","writing-rules.md","forbidden-style.md","profile-goals.md","platforms/linkedin.md","platforms/facebook.md","platforms/instagram.md","platforms/youtube.md"]

def _read_text_files(folder: Path)->list[str]:
    if not folder.exists(): return []
    out=[]
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in {".txt",".md"}:
            text=path.read_text(encoding="utf-8").strip()
            if text: out.append(text)
    return out

def workspace_status(slug:str)->dict:
    try: root=user_root(ROOT,slug)
    except ValueError as exc: return {"status":"error","user":slug,"ready":False,"error":str(exc)}
    if not root.exists(): return {"status":"missing","user":slug,"ready":False}
    missing=[x for x in REQUIRED_PROFILE_FILES if not (root/x).exists()]
    uninitialized=[x for x in REQUIRED_PROFILE_FILES if (root/x).exists() and "Status: not initialized" in (root/x).read_text(encoding="utf-8")]
    ready=not missing and not uninitialized
    return {"status":"ready" if ready else "incomplete","user":slug,"ready":ready,"missing_files":missing,"uninitialized_files":uninitialized,"brand_brain_built":(root/"brand-brain.json").is_file(),"writing_samples":len(_read_text_files(root/"writing-samples")),"approval_required":True,"auto_publish":False}

def _load_json(path:Path,label:str)->dict:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: raise ValueError(f"Invalid {label} JSON in {path}: {exc.msg}") from exc
    if not isinstance(value,dict): raise ValueError(f"Invalid {label}: expected a JSON object in {path}")
    return value

def _load_answers(value):
    if not value: return interactive_answers()
    path=Path(value)
    if not path.is_file(): raise FileNotFoundError(f"Answers file does not exist: {value}")
    try: answers=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise ValueError(f"Could not read onboarding answers: {exc}") from exc
    if not isinstance(answers,dict): raise ValueError("Onboarding answers must be a JSON object.")
    return answers

def _load_user_review_inputs(slug):
    root=user_root(ROOT,slug)
    if not root.exists(): raise FileNotFoundError(f"User workspace does not exist: {slug}")
    ledger=_load_json(root/"claim-ledger.json","claim ledger") if (root/"claim-ledger.json").exists() else None
    return ledger,_read_text_files(root/"writing-samples"),_read_text_files(root/"content-history")

def _error(message,code=2):
    print(json.dumps({"status":"error","error":message},indent=2,ensure_ascii=False)); return code

def main()->int:
    p=argparse.ArgumentParser(prog="credora",description="Credora personal social media manager"); sub=p.add_subparsers(dest="command",required=True)
    start=sub.add_parser("start",help="Create workspace and guided onboarding"); start.add_argument("name"); start.add_argument("--slug"); start.add_argument("--answers")
    setup=sub.add_parser("setup"); setup.add_argument("name"); setup.add_argument("--slug")
    onboard=sub.add_parser("onboard"); onboard.add_argument("user"); onboard.add_argument("--answers"); onboard.add_argument("--overwrite",action="store_true")
    learn=sub.add_parser("learn"); learn.add_argument("user")
    doc=sub.add_parser("doctor"); doc.add_argument("user")
    status=sub.add_parser("status"); status.add_argument("user")
    context=sub.add_parser("context"); context.add_argument("user"); context.add_argument("--platform",choices=["linkedin","facebook","instagram","youtube"],default="linkedin"); context.add_argument("--task",default="post"); context.add_argument("--output")
    cal=sub.add_parser("calendar",help="Create a monthly social content plan"); cal.add_argument("user"); cal.add_argument("--month"); cal.add_argument("--posts",type=int,default=12); cal.add_argument("--platform",choices=["linkedin","facebook","instagram","youtube"],default="linkedin")
    q=sub.add_parser("queue",help="Put a draft into the approval queue"); q.add_argument("user"); q.add_argument("calendar_id"); q.add_argument("draft")
    approve=sub.add_parser("approve",help="Approve a queued draft (does not publish yet)"); approve.add_argument("user"); approve.add_argument("item_id")
    reject=sub.add_parser("reject",help="Reject a queued draft"); reject.add_argument("user"); reject.add_argument("item_id")
    manager=sub.add_parser("manager",help="Show calendar and approval queue status"); manager.add_argument("user")
    check=sub.add_parser("review"); check.add_argument("draft"); check.add_argument("--user"); check.add_argument("--ledger"); check.add_argument("--voice-sample",action="append",default=[]); check.add_argument("--history",action="append",default=[])
    args=p.parse_args()
    try:
        if args.command=="start":
            created=init_user(args.name,args.slug); root=user_root(ROOT,created["slug"]); updated=apply_answers(root,_load_answers(args.answers)); brain=save_for_user(created["slug"],ROOT); result={"status":"ok","user":created["slug"],"workspace":created["workspace"],"updated_files":updated,"brand_brain":brain,"next":f"Add 3+ real writing samples, then run: python scripts/credora.py learn {created['slug']}"}
        elif args.command=="setup": result=init_user(args.name,args.slug); result["next"]=f"python scripts/credora.py onboard {result['slug']}"
        elif args.command=="onboard":
            root=user_root(ROOT,args.user)
            if not root.is_dir(): raise FileNotFoundError(f"User workspace does not exist: {args.user}")
            updated=apply_answers(root,_load_answers(args.answers),overwrite=args.overwrite); result={"status":"ok","user":args.user,"updated_files":updated,"brand_brain":save_for_user(args.user,ROOT)}
        elif args.command=="learn": result=save_for_user(args.user,ROOT)
        elif args.command=="doctor":
            result=doctor(args.user,ROOT); print(json.dumps(result,indent=2,ensure_ascii=False)); return 0 if result.get("healthy") else 2
        elif args.command=="status":
            result=workspace_status(args.user); print(json.dumps(result,indent=2,ensure_ascii=False)); return 0 if result.get("ready") else 2
        elif args.command=="context":
            text=build(args.platform,args.task,args.user)
            if args.output: Path(args.output).write_text(text,encoding="utf-8")
            else: print(text)
            return 0
        elif args.command=="calendar": result=create_calendar(args.user,ROOT,month=args.month,posts=args.posts,platform=args.platform)
        elif args.command=="queue": result=queue_draft(args.user,ROOT,calendar_id=args.calendar_id,draft_file=Path(args.draft))
        elif args.command=="approve": result=set_approval(args.user,ROOT,args.item_id,True)
        elif args.command=="reject": result=set_approval(args.user,ROOT,args.item_id,False)
        elif args.command=="manager": result=manager_status(args.user,ROOT)
        elif args.command=="review":
            draft=Path(args.draft)
            if not draft.is_file(): raise FileNotFoundError(f"Draft file does not exist: {args.draft}")
            ledger=None; voice=[]; history=[]
            if args.user: ledger,voice,history=_load_user_review_inputs(args.user)
            if args.ledger: ledger=_load_json(Path(args.ledger),"claim ledger")
            for f in args.voice_sample: voice.append(Path(f).read_text(encoding="utf-8"))
            for f in args.history: history.append(Path(f).read_text(encoding="utf-8"))
            result=review(draft.read_text(encoding="utf-8"),ledger=ledger,voice_samples=voice,history=history); result["user"]=args.user
        else: return 1
    except (FileExistsError,FileNotFoundError,ValueError,OSError,UnicodeError) as exc: return _error(str(exc))
    print(json.dumps(result,indent=2,ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
