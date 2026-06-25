#!/usr/bin/env python3
"""ingest_s181_batch.py — S181 batch footnote ingest (8 angles, ~93 candidates).

Origin: dev/_research_s181/01..09 harvest JSONs (angle 08 forms library excluded —
discovery seed only). Reviewer A audit: 22/26 sampled passed byte-exact; 4 minor fixes
applied in-place (form text reorder, section label drift, two non-adjacent stitching
issues split or marked with ellipsis). Reviewer B: 89% novel vs existing 15,414-chunk
corpus + 86 footnote_curated rows.

CANONICAL source_id mappings applied per reviewer B collision resolution:
  Cap.279 Education Ordinance       -> cap279_education_ordinance
  EDBC 10/2012 DSS Fee Remission    -> edbc_10_2012_fee_remission
  Existing edbc14_2024_spms reused for EDBC 14/2024 premises maintenance
  Existing edbc22_2024_student_safety reused for EDBC 22/2024 student safety
  Existing supply_teacher_guide reused (drop proposed edb-supply-teacher-guideline)

Exclusions applied:
  Angle 08 (53 form URLs)                          — discovery seed, no verbatim
  09 idx=5 SAG receipt exemption (4 scenarios)     — duplicate of footnote_fn_sag_receipt
  07 idx=12 EDB school safety landing prose        — generic, low value
  07 idx=15 EDB fire equipment landing prose       — generic, low value
  07 idx=16 (= idx=2 FS251 display)                — already covered

In-place fixes applied:
  04 idx=3  CHP notification form  — restored source order, 'For enquiries' moved back to bottom
  04 idx=4  bleach §3.4.1          — section label changed 'Use' -> 'Choice of disinfectants'
  04 idx=12 CHP 22 Oct 2025 letter — '[...]' ellipsis inserted between stitched paragraphs
  07 idx=17 EDBC 22/2024 §2-§5     — SPLIT into TWO entries (§2 framing + §5 30-Nov deadline)

Same mechanism as ingest_s179_footnotes.py / ingest_tips_footnotes.py:
content_type=footnote_curated, route-independent overlay (wikiRepository.searchFootnotes),
id=footnote_fn_<fid>, embed = text + " " + " ".join(keywords).

Modes:
  --self-test (default): embed each + cosine vs representative query (gate LEAD>=0.45) +
                         dup-id check + collision check vs live footnote_curated ids. NO WRITE.
  --execute            : INSPECT before (count + per-id collision) + batch INSERT
                         (merge-duplicates upsert) + INSPECT after.

Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY auto-read from backend/.env.
NOTE: after --execute, restart/redeploy Render (footnote in-memory cache, invalidateFootnoteCache).
"""
import os
import sys
import math
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw  # canonical embed + hash

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

# URL constants
CAP279_URL = "https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/95775/CHN95775.pdf"
TPC_URL = "https://www.edb.gov.hk/attachment/en/teacher/guidelines_tpc/guidelines_en.pdf"
SUPPLY_TEACHER_URL = ("https://www.edb.gov.hk/attachment/en/teacher/appointments-related/"
                     "supply-teachers/supply_teacher_guideline_e.pdf")
COA_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/regulations/codes-of-aid/"
           "code-of-aid-and-related-documents-for-aided-imc-schools/coa_english_1.16.pdf")
DSS_25_URL = ("https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/"
              "applicable-to-primary-secondary/direct-subsidy-scheme/DSS_25-26_e.pdf")
DSS_S4_URL = ("https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/"
              "applicable-to-primary-secondary/direct-subsidy-scheme/index/ss_section4.pdf")
EDBC10_2012_URL = ("https://www.edb.gov.hk/attachment/en/edu-system/primary-secondary/"
                   "applicable-to-primary-secondary/direct-subsidy-scheme/index/edbc12010e.pdf")
EDBC4_2026_URL = "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26004E.pdf"
EDBC8_2020_URL = "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC20008E.pdf"
EDBC9_2019_URL = "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC19009E.pdf"
EDBCM79_URL = ("https://www.edb.gov.hk/attachment/en/student-parents/ncs-students/"
               "support-to-school/EDBCM%20on%20SBP%202025%20(tc).pdf")
AUD76_URL = "https://www.aud.gov.hk/pdf_e/e76ch02.pdf"
CHP_GUIDE_URL = ("https://www.chp.gov.hk/files/pdf/guidelines_on_prevention_of_communicable_diseases_"
                 "in_schools_kindergartens_kindergartens_cum_child_care-centres_child_are_centres.pdf")
SCVPD_URL = "https://www.chp.gov.hk/files/pdf/consensus_recommendation_on_school_closure_due_to_seasonal_influenza.pdf"
CHP_FORM_URL = "https://www.chp.gov.hk/files/pdf/school_notification_form-e.pdf"
CHP_LETTER_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/admin/about-sch/"
                  "diseases-prevention/chp_20251022_eng.pdf")
SFAA_URL = "https://www.hkugac.edu.hk/f/page/416/3846/2526_03a_SFAA_Guidance_Notes.pdf"
WFSFAA_AMOUNT_URL = "https://www.wfsfaa.gov.hk/sfo/en/primarysecondary/tt/general/amount.htm"
EDBC8_2025_NET_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/admin/about-sch-staff/"
                      "net-scheme/EDBC_8_2025_Enhancement%20Measures%20for%20the%20NET%20Scheme.pdf")
NET_GRANT_NOTE_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/admin/about-sch-staff/"
                      "net-scheme/Point-to-note%20for%20receiving%20the%20NET%20Grant_202627.pdf")
NET_PACKAGE_URL = "https://www.edb.gov.hk/attachment/en/common/NET%20package.pdf"
EDBC8_2009_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/admin/about-sch-staff/net-scheme/"
                  "Fringe%20Benefit_aug%202022/Fringe%20Benefit_August%202022_updated/EDBC09008E_082022.pdf")
PNET_ANNEX_URL = ("https://www.edb.gov.hk/attachment/en/curriculum-development/resource-support/net/"
                  "letter_dd_23_Jul_2025_to_principals_PNET_Annex.pdf")
EDBC12_2026_URL = ("https://www.edb.gov.hk/attachment/tc/sch-admin/sch-premises-info/"
                   "sch-premises-maintenance/EDBC26012C.pdf")
EDBC14_2024_URL = ("https://www.edb.gov.hk/attachment/tc/sch-admin/sch-premises-info/"
                   "sch-premises-maintenance/EDBC%2014-2024_Chin_SPMS_final%20(issue).pdf")
EDBC22_2024_URL = ("https://www.edb.gov.hk/attachment/en/sch-admin/admin/about-sch/sch-safety/"
                   "Student%20Safety%20and%20Health/EDBC222024_EN.pdf")
EMSD_RP_URL = "https://www.emsd.gov.hk/filemanager/sc/content_794/Presentation_Duties_RPs.pdf"
EMSD_LE_URL = "https://www.emsd.gov.hk/tc/lifts_and_escalators_safety/leo_intrdctn/index.html"
AUD61_URL = "https://www.aud.gov.hk/pdf_e/e61ch06.pdf"
SAG_URL = "https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/sch-admin-guide/SAG_C_markup.pdf"


# each = dict(fid, source_id, title, topic, url, text, keywords, q)
F = [
    # ============================================================
    # Angle 01 — Teacher Registration (Cap.279 Part IV + TPC + Supply teacher + CoA)
    # ============================================================
    dict(fid="cap279_s42_teach_must_register",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=42",
         text="教學要有咩牌？喺香港學校教書一定要係 registered teacher 定 permitted teacher？"
              "《Education Ordinance (Cap.279)》§42 Teachers to be registered or permitted teachers（註）："
              "Section: 42 Teachers to be registered or permitted teachers. (1) No person shall teach in a school unless he is- (a) a registered teacher; or (b) a permitted teacher. (2) No permitted teacher shall teach in a school otherwise than in accordance with the conditions or limitations specified in the permit to teach issued in respect of such teacher.",
         keywords=["教學要咩牌", "registered teacher", "permitted teacher", "註冊教師", "准用教員",
                   "Cap.279", "§42", "Education Ordinance", "教書資格", "教師註冊",
                   "permit to teach", "法定要求"],
         q="喺香港教書要咩牌 註冊教師 准用教員"),

    dict(fid="cap279_s46_refuse_register",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=46",
         text="點解會拒絕教師註冊？《Education Ordinance (Cap.279)》§46 Grounds for refusal to register teacher（註）："
              "Section: 46 Grounds for refusal to register teacher. The Permanent Secretary may refuse to register an applicant as a teacher if it appears to him that the applicant- (a) is not a fit and proper person to be a teacher; (b) has been convicted of an offence punishable with imprisonment; (c) is a person in respect of whom a permit to teach has previously been cancelled; (d) is medically unfit; (e) does not possess the prescribed qualifications; (f) has attained the age of 70 years; or (g) in making or in connection with any application- (ii) for registration as a manager or a teacher; or (iii) to employ a person as a permitted teacher in a school, has made any statement or furnished any information which is false in any material particular or by reason of the omission of any material particular.",
         keywords=["拒絕教師註冊", "refuse to register", "fit and proper", "刑事紀錄",
                   "convicted", "medically unfit", "70歲", "age of 70", "prescribed qualifications",
                   "Cap.279", "§46", "false declaration", "Permanent Secretary"],
         q="點解教師註冊會被拒絕 fit and proper 70歲"),

    dict(fid="cap279_s47_cancel_register",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=47",
         text="教師取消註冊（de-registration）有咩理由？《Education Ordinance (Cap.279)》§47 Grounds for cancellation of registration of teacher（註）："
              "Section: 47 Grounds for cancellation of registration of teacher. The Permanent Secretary may cancel the registration of a teacher- (a) on any ground specified in section 46 which applies to the teacher, whether or not such ground existed at the time when he was registered as a teacher; (b) if it appears to the Permanent Secretary that the teacher is incompetent; (c) if the teacher has contravened any provision of this Ordinance; (d) if it appears to the Permanent Secretary that the teacher has behaved in any manner which, in the opinion of the Permanent Secretary, constitutes professional misconduct; or (e) if it appears to the Permanent Secretary that the teacher has behaved in any manner which, in the opinion of the Permanent Secretary, is prejudicial to the maintenance of good order and discipline in the school in which the teacher teaches.",
         keywords=["取消教師註冊", "de-registration", "cancellation", "professional misconduct",
                   "incompetent", "失當行為", "Cap.279", "§47", "教師除牌",
                   "good order and discipline", "Permanent Secretary"],
         q="取消教師註冊理由 失當行為"),

    dict(fid="cap279_s48_permit_when",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=48",
         text="幾時可以申請准用教員（PT）？有冇固定比例？《Education Ordinance (Cap.279)》§48 Circumstances in which application to employ permitted teacher may be made（註）："
              "Section: 48 Circumstances in which application to employ permitted teacher may be made. An application to employ a person as a permitted teacher in a school may only be made if the applicant is of the opinion that no suitable registered teacher is available for employment as a teacher in the school.",
         keywords=["准用教員", "permitted teacher", "PT", "申請條件", "no suitable registered teacher",
                   "Cap.279", "§48", "教員短缺", "聘請 PT", "冇固定比例"],
         q="可以請准用教員嘅情況 PT 申請"),

    dict(fid="cap279_s50_pt_school_specific",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=50",
         text="Permit to teach 跟唔跟學校？校長可唔可以加條件？《Education Ordinance (Cap.279)》§50 Permit to teach（註）："
              "Section: 50 Permit to teach. (1) On receiving an application in accordance with section 49, the Permanent Secretary shall make such inquiry as he considers necessary and shall determine the application- (a) by issuing to the management authority of the school concerned a permit in the specified form; or (b) by refusing under section 51 to issue such a permit. (2) A permit to teach issued under subsection (1) shall specify the school in which the permitted teacher may be employed, and may impose such other conditions in respect of the employment of the permitted teacher in the school as the Permanent Secretary thinks fit. (3) The Permanent Secretary shall, if he issues a permit to teach under subsection (1), also issue a copy of the permit to the permitted teacher.",
         keywords=["permit to teach", "准用教員", "學校特定", "school-specific", "條件",
                   "Cap.279", "§50", "PT 跟學校", "imposed conditions", "Permanent Secretary"],
         q="permit to teach 跟唔跟學校 可以加條件嗎"),

    dict(fid="cap279_s52_pt_cancel",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=52",
         text="准用教員離職，個 permit 點？會自動取消嗎？《Education Ordinance (Cap.279)》§52 Grounds for cancellation of permit to teach（註）："
              "Section: 52 Grounds for cancellation of permit to teach. (1) The Permanent Secretary may cancel a permit to teach- (a) on any ground specified in section 51(1)(b), (c) or (d) on which he would have been entitled to refuse to issue a permit to teach, whether or not such ground existed at the time when the permit was issued; or (b) on any ground specified in section 47(b), (c), (d) or (e) which applies to the permitted teacher. (2) A permit to teach shall be deemed to be cancelled- (a) if the permitted teacher ceases to be employed in the school specified in the permit; or (b) if the registration or provisional registration of the school specified in the permit is cancelled.",
         keywords=["permit to teach", "取消准用教員", "離職", "deemed cancelled", "自動取消",
                   "Cap.279", "§52", "ceases to be employed", "permitted teacher", "Permanent Secretary"],
         q="准用教員離職 permit to teach 點 會自動取消"),

    dict(fid="cap279_s61_appeal_21day",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=61",
         text="教師對註冊／取消決定唔服可以幾耐內上訴？《Education Ordinance (Cap.279)》§61 Right of appeal to Appeal Board（註）："
              "Section: 61 Right of appeal to Appeal Board. (1) A person on whom a notice is served under section 60(1) may, within 21 days after the service of the notice, appeal to an Appeal Board against the decision of the Permanent Secretary referred to in the notice, by delivering in duplicate to the secretary of the Appeal Boards Panel a notice of appeal in accordance with subsection (2). (2) Every notice of appeal shall be in writing and shall specify- (a) the decision of the Permanent Secretary in respect of which the appeal is brought; and (b) the grounds on which the appeal is brought.",
         keywords=["上訴", "21日", "21 days", "Appeal Board", "上訴委員會",
                   "Cap.279", "§61", "上訴期", "notice of appeal", "appeal窗"],
         q="教師註冊決定上訴期 21日"),

    dict(fid="tpc_2022_sanction_ladder",
         source_id="edb-guidelines-tpc-2022", title="Guidelines on Teachers' Professional Conduct (2022)",
         topic="general", url=f"{TPC_URL}#page=2",
         text="教師失當行為點處分？EDB 有冇分輕重？《教師專業操守指引 (2022)》Follow-up actions and penalties（註）："
              "For mild misconduct cases, the EDB will issue advisory letters to remind the teachers concerned to refrain from activities that are detrimental to the image of the teaching profession and show respect for the norms of behaviour generally acceptable to society. For more serious and very serious cases, the EDB will issue warning and reprimand letters respectively, specifying that if the teachers concerned misconduct themselves again, the EDB will consider cancelling their teachers' registration pursuant to the Education Ordinance. For extremely serious cases, the EDB will cancel the teachers' registration pursuant to the Education Ordinance. For serious cases that do not warrant cancellation of teacher registration for life, the EDB will stipulate in the cancellation notices that the application for re-registration of the teachers will not be considered within a specified period of time (say, three years). As for teachers with serious misconduct, the practice of \"disqualification for life\" will be adhered to and re-registration will not be allowed in order to ensure the safety of students.",
         keywords=["教師失當行為", "professional misconduct", "advisory letter", "warning",
                   "reprimand", "cancellation", "disqualification for life", "終身停牌",
                   "勸喻信", "警告信", "譴責信", "取消註冊", "重新註冊", "3年", "TPC 2022"],
         q="教師失當行為點處分 4級階梯"),

    dict(fid="tpc_2022_representation_14d",
         source_id="edb-guidelines-tpc-2022", title="Guidelines on Teachers' Professional Conduct (2022)",
         topic="general", url=f"{TPC_URL}#page=2",
         text="可能被取消註冊嘅教師有幾耐時間申辯？《教師專業操守指引 (2022)》Teachers' representations（註）："
              "For cases that may warrant cancellation of registration, the teachers concerned will be informed of the possible cancellation of registration and be invited to submit representations within 14 days with full understanding of the severity of the cases.",
         keywords=["申辯期", "representations", "14日", "14 days", "取消註冊",
                   "cancellation of registration", "TPC 2022", "教師申辯", "陳述",
                   "教師專業操守"],
         q="教師取消註冊前申辯期 14日"),

    dict(fid="supply_pt_min_qual",
         source_id="supply_teacher_guide",
         title="Guidelines for Employment of Substitute Teachers in Aided Schools",
         topic="general", url=f"{SUPPLY_TEACHER_URL}#page=3",
         text="代課准用教員最低學歷要求係咩？《Guidelines for Employment of Substitute Teachers in Aided Schools》footnote 3（註）："
              "The minimum qualification of a Permitted Teacher teaching in schools providing primary and secondary education should be a higher diploma or an associate degree or equivalent.",
         keywords=["准用教員", "permitted teacher", "代課", "最低學歷", "higher diploma",
                   "associate degree", "副學士", "高級文憑", "中小學",
                   "minimum qualification", "PT 學歷"],
         q="准用教員最低學歷要求 副學士 高級文憑"),

    dict(fid="supply_trained_priority",
         source_id="supply_teacher_guide",
         title="Guidelines for Employment of Substitute Teachers in Aided Schools",
         topic="general", url=f"{SUPPLY_TEACHER_URL}#page=8",
         text="請代課老師係咪一定要 trained teachers 優先？《Guidelines for Employment of Substitute Teachers in Aided Schools》§8 General Guidelines for Employment（註）："
              "Priority should be given to trained teachers as far as possible when selecting substitute teachers. Untrained teachers with specified non-standard qualifications or unqualified teachers may be employed as substitute teachers only under very exceptional circumstances (such as subject mismatch or remoteness of the school).",
         keywords=["代課教師", "substitute teachers", "trained teachers", "受訓教師",
                   "untrained", "未受訓", "subject mismatch", "remoteness",
                   "優先聘用", "exceptional circumstances", "代課招聘"],
         q="代課教師 untrained 可唔可以請 受訓優先"),

    dict(fid="supply_blnst_202324",
         source_id="supply_teacher_guide",
         title="Guidelines for Employment of Substitute Teachers in Aided Schools",
         topic="general", url=f"{SUPPLY_TEACHER_URL}#page=4",
         text="2023/24 起新聘月薪臨時教師要唔要考基本法／國安法測試？《Guidelines for Employment of Substitute Teachers in Aided Schools》§4（註）："
              "Starting from the 2023/24 school year, newly-appointed monthly-paid temporary teachers in all aided schools are required to pass the Basic Law and National Security Law Test (BLNST) in order to be considered for appointment.",
         keywords=["BLNST", "基本法測試", "國安法測試", "Basic Law", "National Security Law",
                   "2023/24", "monthly-paid temporary teachers", "月薪臨時教師",
                   "新聘", "aided schools", "代課測試"],
         q="臨時教師基本法測試 2023/24 BLNST"),

    dict(fid="coa_unqualified_teacher",
         source_id="edb-code-of-aid-aided-1-16",
         title="Code of Aid for Aided Schools (Release 1.16)",
         topic="general", url=f"{COA_URL}#page=13",
         text="《資助則例》入面「未獲認可資歷教師」（unqualified teacher）幾時可以請？《Code of Aid for Aided Schools (Release 1.16)》§13.2 footnote 2（註）："
              "This includes registered teacher by merit of ten-year recognised teaching experience and \"unqualified\" teacher i.e. any teacher who does not meet the requirements for appointment as a \"qualified teacher\" as defined in this Code of Aid. The Incorporated Management Committee of an aided school may, if a qualified teacher is not available to fill a vacant teaching post, with full justification, temporarily employ an unqualified teacher except for the teaching of specific subjects which require teachers of special training or qualifications.",
         keywords=["unqualified teacher", "未獲認可資歷", "qualified teacher", "資助則例",
                   "Code of Aid", "IMC", "法團校董會", "10年教學經驗",
                   "臨時聘用", "subject mismatch", "未受訓教師"],
         q="未受訓教師可唔可以請 unqualified teacher 資助則例"),

    # ============================================================
    # Angle 02 — School Registration (Cap.279) + DSS
    # ============================================================
    dict(fid="cap279_s10_school_must_register",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=10",
         text="全港所有學校係咪都要註冊？夜校點計？《Education Ordinance (Cap.279)》§10 Schools to be registered or provisionally registered（註）："
              "(1) Every school shall be registered or provisionally registered. (2) If an aided school or a DSS school provides evening instruction in addition to other education, there shall be deemed to be a separate school in respect of the evening instruction and such separate school shall also be registered or provisionally registered.",
         keywords=["學校註冊", "school registration", "夜校", "evening instruction",
                   "Cap.279", "§10", "provisionally registered", "臨時註冊",
                   "資助學校", "DSS school", "夜間部"],
         q="學校註冊條例 夜校 §10"),

    dict(fid="cap279_s11_application",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=11",
         text="點樣申請學校註冊？要交咩文件？《Education Ordinance (Cap.279)》§11 Application for registration of school（註）："
              "An application for registration of a school shall be- (a) made to the Permanent Secretary in the specified form; and (b) accompanied- (i) by the documents specified in such form; and (ii) if the school is to be operated in or in any part of any premises which are not designed and constructed for the purposes of a school, by the additional documents specified in section 12(1).",
         keywords=["學校註冊申請", "application for registration", "Permanent Secretary",
                   "specified form", "Cap.279", "§11", "申請文件",
                   "非校舍設計", "additional documents", "§12"],
         q="點樣申請學校註冊 要交咩文件"),

    dict(fid="cap279_s13_decision",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=13",
         text="常任秘書長收到學校註冊申請後點處理？《Education Ordinance (Cap.279)》§13 Registration of school（註）："
              "On receiving an application in accordance with section 11, the Permanent Secretary shall make such inquiry as he considers necessary and shall determine the application- (a) by registering the school in respect of which the application is made; or (b) by refusing under section 14 to register the school.",
         keywords=["常任秘書長", "Permanent Secretary", "學校註冊決定", "inquiry",
                   "registration", "refusing", "Cap.279", "§13",
                   "§14", "學校註冊批准"],
         q="常任秘書長處理學校註冊申請決定"),

    dict(fid="cap279_s14_refuse_grounds",
         source_id="cap279_education_ordinance", title="Education Ordinance (Cap.279)",
         topic="general", url=f"{CAP279_URL}#page=14",
         text="EDB 拒絕學校註冊嘅理由有咩？《Education Ordinance (Cap.279)》§14(1)(b)(c)(d) Grounds for refusal to register school（註）："
              "The Permanent Secretary may refuse to register a school if it appears to him- (b) that the proposed school premises are or are likely to be for any reason unsuitable for use for the purposes of a school; (c) that any provision of this Ordinance is being or will be contravened in respect of the school; (d) that the proposed inclusive fee is excessive having regard to the cost of maintaining and operating the school and to the standard of education to be provided;",
         keywords=["拒絕學校註冊", "refuse to register", "校舍不適合", "unsuitable premises",
                   "違反條例", "contravened", "學費過高", "excessive fee",
                   "Cap.279", "§14", "Permanent Secretary", "inclusive fee"],
         q="EDB 拒絕學校註冊理由 校舍 學費"),

    dict(fid="dss_unit_subsidy_233",
         source_id="edb_dss_overview_25_26", title="What are Direct Subsidy Scheme (DSS) schools?",
         topic="general", url=f"{DSS_25_URL}#page=2",
         text="DSS 學校嘅政府資助點計？學費封頂幾多倍？《What are Direct Subsidy Scheme (DSS) schools? (2025/26)》How does the Government subsidize DSS schools?（註）："
              "The amount of recurrent government subsidy received by DSS schools depends on the level of school fees and enrolment. If the fee level does not exceed 2 1/3 of the average unit cost of an aided school place, the amount of recurrent subsidy received for each eligible student will be equal to the average unit cost of an aided school place. Beyond this level, the Government will not provide any recurrent subsidy.",
         keywords=["DSS", "直資", "經常性資助", "recurrent subsidy", "2 1/3",
                   "2⅓", "average unit cost", "資助學位平均單位成本",
                   "學費封頂", "fee cap", "Direct Subsidy Scheme"],
         q="DSS 學校津貼計算 2⅓ 平均單位成本"),

    dict(fid="dss_fee_remission_10pct_50c",
         source_id="edb_dss_overview_25_26", title="What are Direct Subsidy Scheme (DSS) schools?",
         topic="general", url=f"{DSS_25_URL}#page=4",
         text="DSS 學校學費減免要撥幾多？《What are Direct Subsidy Scheme (DSS) schools? (2025/26)》Will disadvantaged students be excluded（註）："
              "DSS schools should set aside at least 10% of their total school fee income for fee remission /scholarship for parents to apply. If a DSS school charges a school fee between 2/3(two-third) and 2 1/3(two and one-third) of the DSS unit subsidy rate, the school should set aside 50 cents for fee remission /scholarship for every additional dollar charged over and above 2/3(two-third) of the DSS unit subsidy rate.",
         keywords=["DSS", "學費減免", "fee remission", "scholarship", "10%",
                   "一成", "set aside", "50 cents", "50仙", "2/3",
                   "2 1/3", "DSS unit subsidy rate", "撥備"],
         q="DSS 學費減免 10% 50仙 撥備"),

    dict(fid="dss_quality_5yr_review",
         source_id="edb_dss_overview_25_26", title="What are Direct Subsidy Scheme (DSS) schools?",
         topic="general", url=f"{DSS_25_URL}#page=6",
         text="DSS 學校嘅質素保證機制係點？《What are Direct Subsidy Scheme (DSS) schools? (2025/26)》How does the Government assure the quality of DSS schools?（註）："
              "DSS schools are required to enter into service agreements with the Government. After having joined the DSS for 5 years, DSS schools are required to undergo a Comprehensive Review to ensure their quality of operation. Moreover, Focus Inspection and External School Review would also be conducted to DSS schools from time to time for quality assurance.",
         keywords=["DSS", "service agreement", "服務協議", "5 years", "5年",
                   "Comprehensive Review", "綜合檢討", "Focus Inspection", "重點視學",
                   "External School Review", "校外評核", "質素保證"],
         q="DSS 質素保證 綜合檢討 5年"),

    dict(fid="dss_s4_unit_cost_basis",
         source_id="edb_ss_section4_dss_subsidy",
         title="Government Subsidy for DSS Secondary Schools (S/S Section 4)",
         topic="general", url=f"{DSS_S4_URL}#page=1",
         text="DSS 中學津貼點計？2001/02 起有冇變？《Government Subsidy for DSS Secondary Schools》S/S Section 4 §1（註）："
              "Schools which are admitted to the DSS will be paid a recurrent government subsidy. The amount of the subsidy will be based on the average unit cost of an aided secondary place. Starting from the 2001/02 school year, a DSS school will continue to receive full subsidy from the Government until its fee level reaches 2 1/3 (two and one-third) of the average unit cost of an aided school place (X). Beyond this level, the Government will not provide any recurrent subsidy.",
         keywords=["DSS 中學", "secondary", "recurrent subsidy", "average unit cost",
                   "資助中學學位平均單位成本", "2001/02", "2 1/3", "2⅓",
                   "full subsidy", "S/S Section 4"],
         q="DSS 中學 average unit cost 津貼上限"),

    dict(fid="edbc10_2012_fr_baseline",
         source_id="edbc_10_2012_fee_remission",
         title="EDBC 10/2012 Fee Remission/Scholarship Schemes in DSS Schools",
         topic="general", url=f"{EDBC10_2012_URL}#page=1",
         text="DSS 學費減免合資格標準要點？係咪可以考慮成績？《EDBC 10/2012》§2 Existing Arrangements（註）："
              "In order to ensure that students will not be deprived of the opportunity to attend DSS schools solely because of their inability to pay fees, each DSS school is required to offer to parents a fee remission/scholarship scheme with a set of eligibility benchmarks no less favourable than the government financial assistance schemes for needy students. In assessing the students' eligibility for fee remission, no factors except the parents' financial situation should be taken into consideration.",
         keywords=["EDBC 10/2012", "DSS", "fee remission", "學費減免", "eligibility benchmarks",
                   "no less favourable", "不得遜於", "政府財政援助",
                   "家庭經濟狀況", "parents' financial situation", "需要學生"],
         q="DSS 學費減免合資格標準"),

    dict(fid="edbc10_2012_reserve_halfyr",
         source_id="edbc_10_2012_fee_remission",
         title="EDBC 10/2012 Fee Remission/Scholarship Schemes in DSS Schools",
         topic="general", url=f"{EDBC10_2012_URL}#page=3",
         text="DSS 學費減免儲備上限係咪有限制？《EDBC 10/2012》§6（註）："
              "Currently, when the reserve for the fee remission/scholarship scheme of a DSS school has reached a cumulative amount that exceeds the school's half-year total fee income due to low utilisation of the scheme, the SMC/IMC should devise a plan on how this specific reserve could be effectively deployed and submit it to the EDB for consideration.",
         keywords=["EDBC 10/2012", "DSS", "fee remission reserve", "減免儲備",
                   "half-year fee income", "半年學費收入", "SMC", "IMC",
                   "校管會", "法團校董會", "deployment plan", "EDB"],
         q="DSS 學費減免儲備上限 半年學費"),

    # ============================================================
    # Angle 03 — NCS Administrative Grant
    # ============================================================
    dict(fid="ncs_composite_2026_intro",
         source_id="EDBC_4_2026_E",
         title="EDBC 4/2026 Composite Support Grant for Non-Chinese Speaking Students",
         topic="general", url=f"{EDBC4_2026_URL}#page=1",
         text="2026/27 起 NCS 津貼有咩變？《EDBC 4/2026 Composite Support Grant for NCS Students》Summary（註）："
              "This circular informs all government schools, aided schools (including special schools), caput schools and schools under the Direct Subsidy Scheme (DSS schools) offering the local curriculum of the integration of the existing Additional Funding for Enhancing Support for Learning and Teaching Chinese for Non-Chinese Speaking Students and the Grant for Supporting Non-Chinese Speaking Students with Special Educational Needs, renamed as the \"Composite Support Grant for Non-Chinese Speaking Students\" (hereafter referred to as \"Composite Support Grant\") starting from the 2026/27 school year and sets out the principles on its use and other relevant details.  This circular supersedes the Education Bureau (EDB) Circular No. 8/2020 on \"New Funding Arrangements for Enhancing Support for Learning and Teaching Chinese for Non-Chinese Speaking Students\" dated 26 June 2020, EDB Circular No. 8/2014 on \"Enhanced Chinese Learning and Teaching for Non-Chinese Speaking Students\" dated 5 June 2014, and EDB Circular No. 9/2019 on \"Grant for Supporting Non-Chinese Speaking Students with Special Educational Needs\" dated 29 March 2019.",
         keywords=["EDBC 4/2026", "Composite Support Grant", "綜合支援津貼",
                   "non-Chinese speaking", "NCS", "非華語學生", "2026/27",
                   "supersedes", "取代", "EDBC 8/2020", "EDBC 8/2014", "EDBC 9/2019"],
         q="NCS 綜合支援津貼 幾時開始 取代邊啲通告"),

    dict(fid="ncs_composite_baseline",
         source_id="EDBC_4_2026_E",
         title="EDBC 4/2026 Composite Support Grant for Non-Chinese Speaking Students",
         topic="general", url=f"{EDBC4_2026_URL}#page=2",
         text="綜合支援津貼基線部分點計？金額幾多？《EDBC 4/2026》§§6-8（註）："
              "The Composite Support Grant consists of three components: the baseline provision, the additional provision and the enrichment provision.\n\n(i) The Baseline Provision\n\nStarting from the 2026/27 school year, schools will be provided with a two-tiered baseline provision based on the number of NCS students admitted.  Details are as follows:\n\nPublic sector ordinary schools and DSS schools offering the local curriculum\nNumber of NCS students | Full-year provision of the baseline provision for each school ($)\n1 to 9 | 230,000\n10 or more | 710,000\n\nSpecial schools\nNumber of NCS students | Full-year provision of the baseline provision for each school ($)\n1 to 5 | 230,000\n6 or more | 710,000\n\nThe amount of the baseline provision will be adjusted in line with the annual Civil Service Pay Adjustment on a school year basis to facilitate schools' appointment of additional teaching/supporting staff.",
         keywords=["Composite Support Grant", "baseline provision", "基線",
                   "230,000", "710,000", "1 to 9", "10 or more",
                   "CSPA", "Civil Service Pay Adjustment", "non-Chinese speaking", "NCS",
                   "special schools", "EDBC 4/2026"],
         q="綜合支援津貼基線金額 1至9名 10名以上"),

    dict(fid="ncs_composite_additional_enrichment",
         source_id="EDBC_4_2026_E",
         title="EDBC 4/2026 Composite Support Grant for Non-Chinese Speaking Students",
         topic="general", url=f"{EDBC4_2026_URL}#page=3",
         text="綜合支援津貼附加同 SEN 增益部分點計？《EDBC 4/2026》§§9-10（註）："
              "(ii) The Additional Provision\n\nApart from the baseline provision, public sector ordinary schools and DSS schools offering the local curriculum admitting 11 or more NCS students, and special schools admitting 10 or more NCS students and with NCS students taking an ordinary school curriculum will be provided with the additional provision based on the number of NCS students.  Details are as follows:\n\nSchool type | NCS students used to calculate total additional provision | Full-year provision of the additional provision for each NCS student ($)\nPublic sector ordinary schools and DSS schools offering the local curriculum | From the 11th student, capped at the 200th | 5,000\nSpecial schools with NCS students taking an ordinary school curriculum | From the 10th student, capped at the 200th | 5,000\n\n(iii) The Enrichment Provision\n\nFor public sector ordinary schools and DSS schools offering the local curriculum, if there are students with SEN among the eligible NCS students admitted, the enrichment provision will be provided at $10,000 for each NCS student with SEN per school year, capped at the 50th such student.",
         keywords=["additional provision", "enrichment provision", "附加部分",
                   "5,000", "10,000", "11th student", "200th",
                   "SEN", "NCS", "非華語", "EDBC 4/2026", "50th student"],
         q="非華語學生 第11名起 每名津貼 SEN 增益"),

    dict(fid="ncs_2tier_small_school",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=2",
         text="學校只有少數非華語學生都有額外津貼嗎？《EDBC 8/2020》§3（註）："
              "Starting from the 2020/21 school year, all schools admitting a relatively small number of NCS students (i.e. 1 to 9 NCS students for ordinary schools and 1 to 5 NCS students for special schools) will be provided with a new two-tiered subsidy.  Application for the funding is not required.  The amount of the funding will be adjusted on a school year basis according to the year-on-year movement of the Composite Consumer Price Index (CCPI) or the annual rate of the Civil Service Pay Adjustment (CSPA).  The additional funding models are as follows:\n\nSchool type | Number of NCS students | Full-year provision of the additional funding ($ million) | Adjustment mechanism\nOrdinary schools and special schools | 1 - 5 | 0.15 | Year-on-year movement of the CCPI\nOrdinary schools | 6 - 9 | 0.30 | Annual rate of the CSPA",
         keywords=["EDBC 8/2020", "small number", "NCS", "non-Chinese speaking",
                   "two-tiered subsidy", "1-5", "6-9", "0.15", "0.30",
                   "CCPI", "CSPA", "免申請", "2020/21"],
         q="學校少數非華語學生 兩級資助"),

    dict(fid="ncs_5tier_table_2019",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=2",
         text="收 10 名或以上非華語學生點計津貼？《EDBC 8/2020》p.2 footnote 4（註）："
              "The amount of the additional funding in the 2019/20 school year is as follows:\n\nOrdinary schools\nNumber of NCS students | Full-year provision of the additional funding ($ million)\n10 - 25 | 0.80\n26 - 50 | 0.95\n51 - 75 | 1.10\n76 - 90 | 1.25\n91 or more | 1.50\n\nSpecial schools\n6 - 9 | 0.65\nThe additional funding model for special schools admitting 10 or more NCS students and with NCS students taking an ordinary school curriculum is the same as that for ordinary schools.\nThe additional funding for special schools admitting 6 or more NCS students but not offering or without any NCS students taking an ordinary school curriculum is $0.65 million.",
         keywords=["EDBC 8/2020", "5-tier", "5級", "NCS", "non-Chinese speaking",
                   "10-25", "0.80", "26-50", "0.95", "51-75", "1.10",
                   "76-90", "1.25", "91 or more", "1.50", "special schools", "0.65"],
         q="學校收 50 名非華語學生 一年幾多錢"),

    dict(fid="ncs_ambit_coordinator",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=3",
         text="非華語學生津貼可以用喺咩？要唔要派老師統籌？《EDBC 8/2020》§5 Use of the Additional Funding（註）："
              "The additional funding should only be used to enhance the support for NCS students' learning of Chinese and create an inclusive learning environment in schools, including strengthening the communication with parents of NCS students and home-school cooperation.  With regard to practical circumstances and learning needs of their NCS students, schools should optimise the use of the additional funding.  All schools provided with the additional funding should assign a dedicated teacher/team to coordinate matters relating to support for NCS students' learning of Chinese and the creation of an inclusive learning environment in schools to ensure that teachers and staff in general understand school policies and measures on supporting NCS students, and to raise their cultural awareness.",
         keywords=["NCS", "non-Chinese speaking", "ambit", "use of additional funding",
                   "中文學習", "共融", "inclusive learning environment", "家校合作",
                   "home-school cooperation", "dedicated teacher", "統籌教師",
                   "EDBC 8/2020", "cultural awareness"],
         q="非華語學生津貼用途 統籌老師"),

    dict(fid="ncs_can_cannot_examples",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=9",
         text="NCS 津貼可唔可以買 iPad、請社工、搞畢業禮？《EDBC 8/2020》Annex 1 General Guidelines on the Use of the Additional Funding（註）："
              "1. Ambit of the additional funding\n• Enhancing the support for non-Chinese speaking (NCS) students' learning of Chinese\n• Creating an inclusive learning environment in schools, including strengthening the communication with parents of NCS students and home-school cooperation\n\n2. Examples of deploying the additional funding within the ambit\n• Appointing additional Chinese Language teachers (full-time/part-time) to implement pull-out learning, split-class/group learning during Chinese Language lessons and/or offer after-school Chinese learning support to NCS students, etc.\n• Appointing additional teachers (full-time/part-time) to relieve the teaching loads of the serving experienced Chinese Language teachers to enhance the support for NCS students' learning of Chinese\n• Appointing teaching assistants to assist teachers in supporting NCS students' learning of Chinese and creating an inclusive learning environment in schools\n• Appointing assistants of different races to strengthen the communication with NCS students and their parents\n• Procuring professional services such as collaborating with non-governmental organisations to organise after-school Chinese learning programmes/activities which promote cultural integration\n• Appointing part-time instructors to organise after-school Chinese learning programmes\n• Purchasing learning and teaching resources (e.g. Chinese picture books, multimedia and electronic learning software, or online Chinese learning platforms which help NCS students learn Chinese)\n• Procuring translation services (e.g. translating school circulars or important matters on school webpages)\n• Organising activities which promote an inclusive learning environment in schools\n• Organising seminars for parents, promoting home-school cooperation and organising activities on parent education\n• Procuring professional services to provide teachers with training on teaching Chinese as a second language and raise their cultural and religious sensitivity\n\n3. Examples of deploying the additional funding not within the ambit\n• Appointing staff not directly related to supporting NCS students' learning of Chinese (e.g. social workers, educational psychologists, speech therapists, guidance personnel, administrative or clerical staff)\n• Appointing additional teaching staff or relevant personnel; however, additional support measures for NCS students are not provided accordingly\n• Purchasing devices, equipment or software (e.g. mobile computing devices, chargers, electronic equipment or computer software) for general purposes\n• Purchasing equipment or tools for handling clerical work of the school\n• Meeting the costs of renovation/works on the school premises\n• Purchasing furniture and equipment\n• Meeting the expenses merely on food, beverages or celebrations/activities without any specific learning objectives and contents (e.g. graduation dinners and parties)\n• Meeting banquet or courtesy-related expenses\n• Meeting in full or in part the expenses on NCS students' visa application or participation in exchange activities outside Hong Kong",
         keywords=["NCS", "non-Chinese speaking", "can use", "cannot use",
                   "within ambit", "not within ambit", "Chinese teachers", "TA",
                   "translation services", "social workers", "iPad", "graduation",
                   "畢業禮", "EDBC 8/2020", "Annex 1"],
         q="NCS 津貼可唔可以買 iPad 請社工 搞畢業禮"),

    dict(fid="ncs_surplus_1yr_cap",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=6",
         text="NCS 津貼用唔晒可以儲幾多？結餘點處理？《EDBC 8/2020》§16 Accounting Arrangements（註）："
              "Schools should maximise the use of the additional funding disbursed each school year in a timely manner so as to support the NCS students in the school year.  Therefore, in principle, schools should not accumulate a substantial surplus of the additional funding.  However, as schools may need to gain experience of supporting NCS students and adjust the support strategies and modes to meet the needs of various NCS students, they may retain part of the additional funding up to an accumulated level not exceeding the total provision of the funding for the school year.  Any surplus in excess should be returned to EDB.  Based on schools' audited annual accounts, EDB will claw back any surplus in excess.  Schools should not transfer the additional funding/surplus to other ledgers.",
         keywords=["NCS", "non-Chinese speaking", "surplus", "結餘",
                   "total provision", "claw back", "追回", "transfer to other ledgers",
                   "audited annual accounts", "EDBC 8/2020", "accumulate"],
         q="NCS 津貼結餘 上限 點處理"),

    dict(fid="ncs_school_plan_30nov",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=6",
         text="NCS 津貼學校計劃書幾時要交？要 IMC 通過嗎？《EDBC 8/2020》§18 Evaluation, Accountability and Support（註）："
              "All schools provided with the additional funding are required to plan their support measures for NCS students early and review them on an ongoing basis.  They should also submit to EDB a school plan and a school report on the deployment of the funding and relevant support measures endorsed by their Incorporated Management Committees/School Management Committees each school year, summarising the implementation and evaluating the effectiveness of relevant measures.  This will serve as reference for planning the support measures for the following school year.  Following the prevailing procedure, the school report of the preceding school year (if applicable), as well as the school plan for the new school year, signed by the school supervisor should be submitted on or before 30 November each year.  In addition, starting from the 2021/22 school year, schools are required to provide a bilingual summary in both Chinese and English, elucidating how they have supported NCS students' learning of Chinese and created an inclusive learning environment in the schools in the preceding school year on or before 30 November each year.  The summary should be uploaded to their school webpages for parents' reference.",
         keywords=["NCS", "non-Chinese speaking", "school plan", "school report",
                   "30 November", "11月30日", "IMC", "SMC", "endorsed",
                   "bilingual summary", "school webpage", "EDBC 8/2020"],
         q="NCS 津貼學校計劃書 幾時要交 IMC"),

    dict(fid="ncs_report_31jul_midsept",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=4",
         text="非華語學生人數幾時要報教育局？《EDBC 8/2020》§11 Submission of NCS Students' Information（註）："
              "Schools are required to complete and return the form on \"Estimated Number of Eligible NCS Students in the New School Year\" (the templates are at Annex 2 and Annex 3) and submit relevant information where necessary by 31 July each year.  In addition, schools should submit via WebSAMS accurate information of all students (including information of NCS students verified by schools) as at the reference date specified in the Enrolment Survey (usually in mid-September).",
         keywords=["NCS", "non-Chinese speaking", "estimated number", "31 July",
                   "7月31日", "Enrolment Survey", "WebSAMS", "mid-September",
                   "9月中", "EDBC 8/2020", "申報"],
         q="非華語學生人數 幾時要報教育局"),

    dict(fid="ncs_sen_3tier",
         source_id="EDBC_9_2019_E",
         title="EDBC 9/2019 Grant for Supporting NCS Students with SEN",
         topic="general", url=f"{EDBC9_2019_URL}#page=2",
         text="非華語 SEN 學生額外津貼幾多？點分級？《EDBC 9/2019》§4（註）："
              "The NCS-SEN Grant is a recurrent cash grant and will be disbursed under a three-tier structure according to the number of NCS students with SEN enrolled in each school.  The grant rates for the 2019/20 school year are shown in the table below, and they will be adjusted annually according to the change in the Composite Consumer Price Index:\n\nTier | Number of NCS students with SEN | Grant rate\n1 | 1 to 9 | $100,000\n2 | 10 to 25 | $200,000\n3 | 26 or more | $300,000\n\n[Note (updated 19 August 2025): The grant rates will not be adjusted according to the Composite Consumer Price Index in the 2025/26 school year.]",
         keywords=["NCS-SEN", "non-Chinese speaking", "SEN", "three-tier",
                   "三級", "100,000", "200,000", "300,000", "1-9", "10-25",
                   "26 or more", "CCPI", "EDBC 9/2019", "2025/26 凍結"],
         q="非華語 SEN 學生 額外津貼 幾多錢"),

    dict(fid="ncs_sen_12mo_cap",
         source_id="EDBC_9_2019_E",
         title="EDBC 9/2019 Grant for Supporting NCS Students with SEN",
         topic="general", url=f"{EDBC9_2019_URL}#page=4",
         text="NCS-SEN 津貼結餘可以儲幾多？《EDBC 9/2019》§12（註）："
              "Schools should fully utilise the NCS-SEN Grant to address adjustment and integration problems with respect to their emotions, communication, socialisation and transition encountered by the students concerned of the relevant school year, and establish a regular mechanism to monitor expenditures under this additional grant.  As such, schools in general should not have a large surplus from the grant.  Aided, caput and DSS schools may retain an unspent balance up to 12 months' provision of the grant in a school year and carry it forward to the next school year.  Any surplus balance in excess of the capped amount should be clawed back by the EDB, which will make clawback arrangement according to the schools' audited annual accounts.",
         keywords=["NCS-SEN", "non-Chinese speaking", "SEN", "surplus",
                   "結餘", "12 months", "12個月", "carry forward",
                   "claw back", "追回", "audited annual accounts", "EDBC 9/2019"],
         q="NCS-SEN 津貼結餘 12個月"),

    dict(fid="ncs_sbp_26360_class",
         source_id="EDBCM_79_2025_TC",
         title="教育局通函第79/2025號 非華語學生暑期銜接課程",
         topic="general", url=f"{EDBCM79_URL}#page=3",
         text="非華語學生暑期銜接課程每班幾多錢？餘款點處理？《教育局通函第79/2025號》§9 課程津貼（註）："
              "本局會按申請學校的參加學生人數及分組安排，批准學校開辦的班數，並向學校發放有關津貼。2025 年的津貼額為每班 26,360 元。學校在課程完結時須核實有關津貼的收支結餘，如有未使用的津貼餘款，教育局將根據學校提交經審核的帳目收回截至 2025 年 8 月 31 日的餘款。餘款不可結轉至下一學年使用。學校不得將課程津貼及／或餘款調往其他帳目。學校亦須按教育局發出的相關《行政指引》運用有關津貼，否則學校須向教育局全數歸還所獲得的津貼。",
         keywords=["非華語", "NCS", "暑期銜接課程", "Summer Bridging Programme", "SBP",
                   "26,360", "每班", "2025年8月31日", "餘款", "不可結轉",
                   "EDBCM 79/2025", "課程津貼"],
         q="非華語 暑期銜接課程 每班幾多錢 餘款"),

    dict(fid="ncs_sbp_60hr_min",
         source_id="EDBCM_79_2025_TC",
         title="教育局通函第79/2025號 非華語學生暑期銜接課程",
         topic="general", url=f"{EDBCM79_URL}#page=2",
         text="非華語暑期班開班條件係咩？《教育局通函第79/2025號》§4（註）："
              "參與的學校必須作以下的安排：\n(i) 在暑假期間免費提供每班總時數不少於 60 小時的課程，並預留後備日子，以便在有需要時（例如受惡劣天氣影響而停課）安排補課，以確保每班總時數不少於 60 小時；\n(ii) 普通學校每班學生人數平均約 15 名，參與人數下限為 10 名來自本校／及他校的非華語學生；而特殊學校的參與人數下限則為 5 名非華語學生；及\n(iii) 邀請非華語學生的家長及監護人（每名學生的家長或監護人不多於 2 名）陪同學生上課及／或參加學習活動，促進家校合作。",
         keywords=["非華語", "NCS", "暑期銜接課程", "60小時", "15名", "10名",
                   "5名", "普通學校", "特殊學校", "家長陪同",
                   "EDBCM 79/2025", "開班條件"],
         q="非華語暑期班 開班要幾多人 幾多小時"),

    dict(fid="ncs_sbp_questionnaire_30nov",
         source_id="EDBCM_79_2025_TC",
         title="教育局通函第79/2025號 非華語學生暑期銜接課程",
         topic="general", url=f"{EDBCM79_URL}#page=3",
         text="暑期銜接課程問卷同學校報告幾時要交？《教育局通函第79/2025號》§10（註）："
              "為蒐集學校對課程的意見及評估課程的整體成效，教育局會進行督導訪校，並在課程完結後以問卷方式蒐集持分者的意見。學校須在 2025 年 9 月 30 日或之前填妥問卷並連同課程內容交回教育局。本局會另函通知學校有關安排。此外，根據「優化學校發展與問責架構」，參與學校須檢視該課程，並在學校報告中列出實施該課程的詳情（包括課堂安排、參與的非華語學生及其家長人數）、檢討結果，以及該課程對改善非華語學生學習中文的成效評估等。學校須在 2025 年 11 月 30 日或之前將學校報告上載至學校網頁。",
         keywords=["非華語", "NCS", "暑期銜接課程", "問卷", "學校報告",
                   "9月30日", "11月30日", "2025年", "上載學校網頁",
                   "督導訪校", "EDBCM 79/2025"],
         q="暑期銜接課程 問卷 學校報告 幾時要交"),

    dict(fid="ncs_kg_5tier_201920",
         source_id="AUD_e76ch02",
         title="Audit Report No.76 Ch.2 Education Support Measures for NCS Students",
         topic="kindergarten", url=f"{AUD76_URL}#page=10",
         text="幼稚園收非華語學生點計津貼？5級制幾多錢？《Audit Report No.76 Ch.2》Table 2 (2019/20)（註）："
              "Starting from 2019/20, a 5-tiered grant ranging from $50,000 to an amount comparable to the annual salary of two basic-rank kindergarten teachers is provided per year to kindergartens according to the number of NCS students admitted (see Table 2):\n\nNo. of NCS students admitted | Amount of Grant ($)\n1 - 4 | 50,000\n5 - 7 | 198,960\n8 - 15 | 397,920\n16 - 30 | 596,880\n≥31 | 795,840",
         keywords=["NCS", "非華語", "幼稚園", "kindergarten", "Scheme-KG",
                   "5-tier", "5級", "50,000", "198,960", "397,920",
                   "596,880", "795,840", "2019/20", "Audit Report 76"],
         q="幼稚園 收非華語學生 點計津貼 5級制"),

    dict(fid="ncs_special_school_matrix",
         source_id="AUD_e76ch02",
         title="Audit Report No.76 Ch.2 Education Support Measures for NCS Students",
         topic="general", url=f"{AUD76_URL}#page=10",
         text="特殊學校收非華語學生點分津貼？《Audit Report No.76 Ch.2》§2.2(c)（註）："
              "Special schools admitting 1 to 5 NCS students.  These schools might apply for a grant of $50,000 per year on a need basis for organising after-school support programmes in learning the Chinese language for their NCS students;\nSpecial schools admitting 6 to 9 NCS students with NCS students taking an ordinary school curriculum.  A grant of $650,000 is provided per year to each school;\nSpecial schools admitting 10 or more NCS students with NCS students taking an ordinary school curriculum.  Same as ordinary primary and secondary schools offering local curriculum and admitting 10 or more NCS students, the amount of grant is determined by the 5-tiered funding mechanism;\nSpecial schools admitting 6 or more NCS students without any NCS students taking an ordinary school curriculum.  A grant of $650,000 is provided per year to each school.",
         keywords=["NCS", "非華語", "special schools", "特殊學校",
                   "1 to 5", "50,000", "6 to 9", "650,000",
                   "10 or more", "ordinary school curriculum", "Audit Report 76"],
         q="特殊學校 收 NCS 學生 津貼點分"),

    dict(fid="ncs_definition_home_language",
         source_id="EDBC_8_2020_E",
         title="EDBC 8/2020 New Funding Arrangements for NCS Students",
         topic="general", url=f"{EDBC8_2020_URL}#page=1",
         text="邊個算非華語學生？寄宿生算唔算？《EDBC 8/2020》footnote 1 + Annex 2/3 footnote（註）："
              "For the planning of educational support measures, students whose spoken language at home is not Chinese are broadly categorised as NCS students.\n\n[Annex 3 / Annex 2 elaboration:] As regards special schools, if a student's spoken language at home cannot be identified due to special circumstances (e.g. the student does not communicate in spoken language), they can make reference to the spoken language used by his/her parent(s) and determine whether the student is an NCS student accordingly.  For students whose spoken language at home is unknown or not applicable (e.g. boarding students), generally speaking, they should not be categorised as NCS students by schools.",
         keywords=["NCS definition", "非華語定義", "spoken language at home",
                   "家庭常用語言", "boarding students", "寄宿生", "special schools",
                   "EDBC 8/2020", "NCS 資格"],
         q="邊個算非華語學生 定義 寄宿生"),

    # ============================================================
    # Angle 04 — Communicable Disease Prevention + School Closure (CHP/SCVPD)
    # ============================================================
    dict(fid="chp_class_closure_ili_20pct",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=32",
         text="幾多 percent 學生病要停課？《Guidelines on Prevention of Communicable Diseases in Schools》§5.7.4 School closure（註）："
              "5.7.4 School closure\nCHP may consider advising the affected schools/centres to suspend classes for a period of time, based on factors such as the number of children affected, the number of children with severe illness and number of hospitalisations, the progression of the outbreak and whether it is responsive to control measures, etc. School/centre staff should provide the necessary arrangement.\nFor influenza/influenza-like illness outbreaks, reference will also be taken from the indicators recommended by CHP's Scientific Committee on Vaccine Preventable Diseases in August 2018*.\n*The Scientific Committee on Vaccine Preventable Diseases recommended that closure of an individual school with influenza/influenza-like illness outbreaks may be considered taking reference from the following indicators: (i) any death of healthy children in the school due to influenza; (ii) two or more children required intensive care unit admission due to influenza; or (iii) influenza-like illness attack rate among children is 20% or more. In addition to the above indicators, factors including the number of staff affected (which may potentially affect operation of the school), epidemic trend of the outbreak and effectiveness of control measures etc., should also be taken into consideration for advising school closure during an influenza/influenza-like illness outbreak. The recommended closure duration is 7 days.",
         keywords=["停課", "school closure", "20%", "ILI", "influenza-like illness",
                   "attack rate", "ICU", "2 or more", "7 days", "7日",
                   "SCVPD", "流感", "CHP", "2018年8月", "scvpd"],
         q="幾多percent學生病要停課 流感"),

    dict(fid="chp_outbreak_def_3rti_2hfmd",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=28",
         text="甚麼算傳染病爆發？《Guidelines on Prevention of Communicable Diseases in Schools》§5.1.1（註）："
              "5.1 What does an outbreak of communicable disease mean?\n5.1.1 If children or staff develop similar symptoms one after another and the incidence is higher than usual, occurrence of outbreak is suspected. Examples are three or more students in the same class develop symptoms of respiratory tract infections; and two or more students in the same class (or had studied in the same setting in case of kindergarten or child care centres] develop symptoms of hand, foot and mouth disease in succession within a short time.",
         keywords=["傳染病爆發", "outbreak", "3 or more", "三個", "RTI",
                   "respiratory tract infection", "2 or more", "兩個",
                   "HFMD", "hand foot and mouth", "手足口", "same class",
                   "CHP", "outbreak threshold"],
         q="甚麼算傳染病爆發 3個 同班"),

    dict(fid="chp_ceno_contact",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=34",
         text="報傳染病打邊個電話？《Guidelines on Prevention of Communicable Diseases in Schools》§6.3（註）："
              "6.3 Notification of outbreaks of communicable diseases in schools/centres (Appendix 2)\nCentral Notification Office (CENO)\nCentre for Health Protection\nDepartment of Health\nTel: 2477 2772\nFax: 2477 2770",
         keywords=["CENO", "Central Notification Office", "中央通報辦事處",
                   "Centre for Health Protection", "衞生防護中心",
                   "2477 2772", "2477 2770", "報傳染病", "電話",
                   "fax", "Department of Health"],
         q="報傳染病打邊個電話 CENO"),

    # FIX idx=3: Restored source order — 'For enquiries' moved back to bottom
    dict(fid="chp_form_routing",
         source_id="chp_notification_form_2025oct",
         title="Suspected Infectious Disease Outbreak NOTIFICATION FORM (CHP)",
         topic="general", url=CHP_FORM_URL,
         text="幼稚園爆發傳染病要同邊個部門報？《Suspected Infectious Disease Outbreak NOTIFICATION FORM (2025 Oct)》form footer（註）："
              "Suspected Infectious Disease Outbreak in School / Kindergarten / KG-cum CCC / Child Care Centre — NOTIFICATION FORM\nTo: Central Notification Office (CENO), Centre for Health Protection (Fax: 2477 2770) (Email: diseases@dh.gov.hk)\n* School / KG — fax copy to School Development Section of Education Bureau in respective district\n† KG-cum-CCC — fax copy to Joint Office for Kindergartens and Child Care Centres of Education Bureau (Fax: 3107 2180)\n‡ CCC — fax copy to Child Care Centres Advisory Inspectorate of Social Welfare Department (Fax: 2591 9113)\nFor enquiries, please call 2477 2772",
         keywords=["notification form", "通報表格", "CENO", "diseases@dh.gov.hk",
                   "2477 2770", "School Development Section", "KG-cum-CCC",
                   "3107 2180", "CCC", "2591 9113", "幼稚園爆發",
                   "Social Welfare Department", "School / Kindergarten"],
         q="幼稚園爆發傳染病 fax 同邊個 department 報"),

    # FIX idx=4: Section label changed to 'Choice of disinfectants'
    dict(fid="chp_bleach_dilution",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=19",
         text="漂白水點溝消毒課室？《Guidelines on Prevention of Communicable Diseases in Schools》§§3.4.1-3.4.2（註）："
              "3.4.1 Choice of disinfectants\n• 1 in 99 diluted household bleach (5.25%) is sufficient for general cleaning purpose and 1 in 49 diluted household bleach should be used for places contaminated with respiratory secretions, vomitus or excreta.\n3.4.2 General cleansing\n• Clean and disinfect the school premises including classrooms, kitchen canteen, toilets, bathrooms, and school buses with 1 in 99 diluted household bleach (mixing 1 part of 5.25% bleach with 99 parts of water), wait until the disinfectant dries up, then rinse with water and keep dry.\n• Clean and disinfect frequently touched surfaces, such as furniture, toys and commonly shared items (such as computer keyboards) at least daily by using appropriate disinfectant (e.g. 1 in 99 diluted household bleach by mixing 1 part of 5.25% bleach with 99 parts of water for non-metalic surfaces; or 70% alcohol for metallic surfaces), leave for 15-30 minutes, and then rinse with water and keep dry.\n• Use absorbent disposable towels to wipe away obvious contaminants such as respiratory secretions, vomitus or excreta, then disinfect the surface and neighbouring areas with appropriate disinfectant (e.g. 1 in 49 diluted household bleach by mixing 1 part of 5.25% bleach with 49 parts of water for non-metalic surfaces; or 70% alcohol for metallic surfaces), leave for 15-30 minutes and then rinse with water and keep dry.",
         keywords=["漂白水", "bleach", "5.25%", "1:99", "1:49", "稀釋",
                   "70% alcohol", "酒精", "metallic", "非金屬",
                   "15-30 minutes", "general cleaning", "respiratory secretions",
                   "vomitus", "excreta", "Choice of disinfectants"],
         q="漂白水點溝消毒課室 1:99 1:49"),

    dict(fid="chp_bleach_appendix9_ppm",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=46",
         text="1:99 漂白水係幾多 ppm？《Guidelines on Prevention of Communicable Diseases in Schools》Appendix 9（註）："
              "Appendix 9 — Procedures of preparing/using diluted bleach\nRecommended Use of Household Bleach (5.25% hypochlorite solution)\nDilution ratio 1 in 4 | Concentration 10,000 ppm (1%) | Preparation: One part of household bleach (5.25% hypochlorite solution) in 4 parts of water | Usage: For facilities contaminated with blood spillage\nDilution ratio 1 in 49 | Concentration 1,000 ppm (0.1%) | Preparation: One part of household bleach (5.25% hypochlorite solution) in 49 parts of water | Usage: For surfaces or articles contaminated with vomitus, excreta or secretions\nDilution ratio 1 in 99 | Concentration 500 ppm (0.05%) | Preparation: One part of household bleach (5.25% hypochlorite solution) in 99 parts of water | Usage: For general environmental cleaning",
         keywords=["bleach", "漂白水", "1:4", "1:49", "1:99",
                   "10,000 ppm", "1,000 ppm", "500 ppm", "blood spillage",
                   "血液", "vomitus", "general cleaning", "Appendix 9",
                   "5.25% hypochlorite"],
         q="1:99 漂白水係幾多 ppm"),

    dict(fid="chp_sick_leave_diseases",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=50",
         text="手足口病要請幾多日假？麻疹呢？《Guidelines on Prevention of Communicable Diseases in Schools》Appendix 13（註）："
              "Appendix 13 — Recommendation on sick leave duration for common childhood infections\nAcute conjunctivitis: Until no abnormal secretion from the eyes\nChickenpox*: About one week or until all vesicles have dried up\nHand, foot and mouth disease: Until all vesicles dry up or as advised by the doctor. If enterovirus 71 is confirmed to be the pathogen, take 2 more weeks of sick leave after all vesicles have dried up\nMeasles*: 4 days after the day of appearance of rash\nMumps*: 5 days after the day of appearance of gland swelling\nRubella*: 7 days after the day of appearance of rash\nScarlet fever*: Until fever down and 24 hours after starting of appropriate antibiotic\nViral gastroenteritis: Until 48 hours after the last episode of diarrhoea or vomiting\nWhooping cough*: 5 days from starting the antibiotic course or as advised by the doctor\nCoronavirus disease 2019*: Until symptoms subside or as advised by the doctor\nNote: Diseases marked with asterisk (*) should be reported to the Centre for Health Protection as required by the law.",
         keywords=["sick leave", "病假", "手足口", "HFMD", "EV71",
                   "Chickenpox", "水痘", "Measles", "麻疹", "Mumps", "腮腺炎",
                   "Rubella", "風疹", "Scarlet fever", "猩紅熱", "COVID-19",
                   "Appendix 13", "return to school"],
         q="手足口病 要請幾多日假"),

    dict(fid="chp_hfmd_ev71_2wk",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=31",
         text="EV71 確診學校點處理？《Guidelines on Prevention of Communicable Diseases in Schools》§5.7.3（註）："
              "5.7.3 Outbreak of hand, foot and mouth disease and enterovirus 71 infection\n• Advise sick children and staff to stay at home and seek medical advice immediately if they develop symptoms. If hand, foot and mouth disease is confirmed, advise them to stay at home until all vesicles have dried up or as advised by the doctor. If one case is confirmed to be enterovirus 71 infection, all affected children in the schools/centres should take two more weeks of sick leave after all vesicles have dried up.",
         keywords=["HFMD", "hand foot and mouth", "手足口", "EV71",
                   "enterovirus 71", "腸病毒71", "2 more weeks", "額外兩星期",
                   "vesicles", "水疱", "outbreak management", "stay at home"],
         q="EV71 確診學校處理 額外2星期"),

    dict(fid="chp_rti_fever_2day",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=31",
         text="發燒退咗幾耐先可以返學？《Guidelines on Prevention of Communicable Diseases in Schools》§5.7.2（註）："
              "5.7.2 Outbreak of respiratory tract infection\n• If children and staff develop symptoms of influenza such as fever, sore throat or cough, advise them to put on a well-fitted surgical mask and seek medical advice immediately.\n• Require staff and students to notify the schools/centres if they develop influenza symptoms or are admitted to hospital.\n• Require the sick to stay at home for rest until symptoms have improved and fever has subsided for at least 2 days.\n• Enhance health surveillance for other children by, for example, measuring body temperature.\n• Switch on exhaust fans and open windows as far as possible to improve ventilation.\n• Avoid group activities during an outbreak.\n• Minimise staff movement and arrange the same group of staff to take care of the same group of children as far as possible.",
         keywords=["RTI", "respiratory tract infection", "fever subsided",
                   "2 days", "2日", "退燒", "return to school", "返學",
                   "surgical mask", "口罩", "ventilation", "exhaust fans",
                   "influenza", "流感"],
         q="發燒退咗幾耐先可以返學"),

    dict(fid="chp_age_2day_rule",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=30",
         text="嘔吐肚屙爆發點處理？《Guidelines on Prevention of Communicable Diseases in Schools》§5.7.1（註）："
              "5.7.1 Outbreak of acute gastroenteritis or food poisoning\n• Disinfect articles or places contaminated by excreta or vomitus.\n• Clean and disinfect toilets with 1 in 49 diluted household bleach (mixing 1 part of 5.25% bleach with 49 parts of water).\n• Sick staff, especially the food-handlers, should take sick leave to prevent the spread of disease.\n• Keep affected children and staff away from schools/centres until their diarrhoea or vomiting has subsided for at least 2 days or as advised by the doctor.",
         keywords=["acute gastroenteritis", "急性腸胃炎", "food poisoning",
                   "食物中毒", "嘔吐", "肚屙", "diarrhoea", "vomiting",
                   "1 in 49", "1:49", "bleach", "2 days", "food-handlers",
                   "Norovirus"],
         q="嘔吐肚屙爆發點處理"),

    dict(fid="chp_outbreak_disinfect",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=30",
         text="爆發後課室點消毒？《Guidelines on Prevention of Communicable Diseases in Schools》§5.6（註）："
              "5.6 Environmental disinfection during outbreak of communicable diseases\n• Disinfect furniture, floor and toilets with appropriate disinfectant (e.g. mixing 1 part of 5.25% bleach with 49 parts of water for non-metallic surface or using 70% alcohol for metallic surface); leave for 30 minutes before rinsing with water and mopping dry; pay special attention to disinfection of toilets, surfaces that are frequently touched such as door knobs and handrails.\n• Use highly absorbent materials to clean up surfaces contaminated by vomitus or excreta preliminarily before performing the above disinfection procedures.",
         keywords=["outbreak disinfection", "爆發消毒", "1 in 49", "1:49",
                   "70% alcohol", "metallic surface", "non-metallic",
                   "30 minutes", "door knobs", "門柄", "handrails",
                   "扶手", "bleach"],
         q="爆發後課室點消毒"),

    dict(fid="scvpd_closure_rationale",
         source_id="scvpd_school_closure_2018aug",
         title="SCVPD Consensus Recommendations on School Closure due to Seasonal Influenza",
         topic="general", url=f"{SCVPD_URL}#page=3",
         text="流感停課準則邊個專家委員會訂？點解係 7 日？《SCVPD Consensus Recommendations》§§9-11（註）："
              "9. Based on the review of the local epidemiology, scientific literature and overseas practice, SCVPD recommends that closure of an individual school with influenza/influenza-like illness outbreaks may be considered taking reference from the following indicators:\n(a) Any death of healthy children in the school due to influenza,\n(b) Two or more children required intensive care unit admission due to influenza, or\n(c) Influenza-like illness attack rate among children is 20% or more.\n10. In addition to the above indicators, factors including the number of staff affected (which may potentially affect operation of the school), epidemic trend of the outbreak and effectiveness of control measures etc., should also be taken into consideration for advising school closure during an influenza/influenza-like illness outbreak.\n11. SCVPD also noted that there is no international consensus/guidelines on the optimum closure duration regarding closure of an individual school due to influenza outbreak. As influenza has an incubation period of about 1-4 days and a communicable period of about 3-5 days in general, SCVPD considers that 7 days of school closure is appropriate for interrupting influenza transmission within the affected school.",
         keywords=["SCVPD", "Scientific Committee", "Vaccine Preventable Diseases",
                   "school closure", "stop class", "influenza", "ILI",
                   "20%", "2 ICU", "1-4 days incubation", "3-5 days communicable",
                   "7 days", "7日", "primary source"],
         q="流感停課準則 邊個專家委員會 7日"),

    # FIX idx=12: Insert '[...]' ellipsis between non-adjacent paragraphs
    dict(fid="chp_letter_flu_2025oct22",
         source_id="chp_letter_flu_2025oct22",
         title="Letter to Principal — Prevention of Seasonal Influenza in Schools (2025-10-22)",
         topic="general", url=CHP_LETTER_URL,
         text="2025 流感季學校要做啲咩？《CHP Letter to Principal 22 Oct 2025》（註）："
              "If schools notice an increase in fever or respiratory illnesses among students or staff, school should report promptly to the Central Notification Office of the Centre for Health Protection (CHP) (Tel: 2477 2772; Fax: 2477 2770; Email: diseases@dh.gov.hk) for prompt epidemiological investigations and appropriate control measures.\n\n[...]\n\nSchools are advised to enhance health surveillance for students, such as measuring body temperature when they enter the school. They should require sick students and staff to stay home until symptoms subside and fever has been absent for at least two days. If students and staff develop ILI symptoms such as fever, sore throat or cough at the school, they should wear a well-fitting surgical mask and seek medical advice promptly.",
         keywords=["CHP letter", "2025-10-22", "Albert AU", "flu season",
                   "fever", "respiratory illnesses", "CENO", "2477 2772",
                   "diseases@dh.gov.hk", "2 days", "ILI", "surgical mask",
                   "health surveillance"],
         q="2025 流感季學校要做啲咩"),

    dict(fid="chp_notifiable_diseases_list",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=35",
         text="邊啲傳染病要法定通報？《Guidelines on Prevention of Communicable Diseases in Schools》Appendix 1（註）："
              "Appendix 1 — Statutory notifiable communicable diseases:\nAcute poliomyelitis; Amoebic dysentery; Anthrax; Bacillary dysentery; Botulism; Chickenpox; Chikungunya fever; Cholera; Community-associated methicillin-resistant Staphylococcus aureus infection; Coronavirus Disease (COVID-19); Creutzfeldt-Jakob disease; Dengue fever; Diphtheria; Enterovirus 71 infection; Food poisoning; Haemophilus influenzae type b infection (invasive); Hantavirus infection; Invasive pneumococcal disease; Japanese encephalitis; Legionnaires' disease; Leprosy; Leptospirosis; Listeriosis; Malaria; Measles; Melioidosis; Meningococcal infection (invasive); Middle East Respiratory Syndrome; Monkeypox; Mumps; Novel influenza A infection; Paratyphoid fever; Plague; Psittacosis; Q fever; Rabies; Relapsing fever; Rubella and congenital rubella syndrome; Scarlet fever; Severe Acute Respiratory Syndrome; Shiga toxin-producing Escherichia coli infection; Smallpox; Streptococcus suis Infection; Tetanus; Tuberculosis; Typhoid fever; Typhus and other rickettsial diseases; Viral haemorrhagic fever; Viral hepatitis; West Nile Virus Infection; Whooping cough; Yellow fever; Zika Virus Infection.\nUpdated list: https://cdis.chp.gov.hk/CDIS_CENO_ONLINE/disease.html",
         keywords=["statutory notifiable", "法定通報", "communicable diseases",
                   "傳染病", "Chickenpox", "COVID-19", "Measles", "Mumps",
                   "Rubella", "Scarlet fever", "Tuberculosis", "結核病",
                   "Appendix 1", "CDIS"],
         q="邊啲傳染病要法定通報"),

    dict(fid="chp_bed_spacing_1m",
         source_id="chp_prev_cd_schools_2025nov",
         title="Guidelines on Prevention of Communicable Diseases in Schools",
         topic="general", url=f"{CHP_GUIDE_URL}#page=22",
         text="幼稚園床位距離要求係幾多？《Guidelines on Prevention of Communicable Diseases in Schools》§3.4.7（註）："
              "3.4.7 Miscellaneous\n• If beds are provided, keep appropriate distance between beds or groups of beds (not less than 1 metre) to reduce the chance of transmission of infective agents by droplets.",
         keywords=["beds", "床", "1 metre", "1米", "幼稚園",
                   "kindergarten", "CCC", "child care centre", "droplets",
                   "nap room", "睡房", "spacing"],
         q="幼稚園床位距離要求 1米"),

    # ============================================================
    # Angle 05 — Fee Remission + Textbook Assistance (SFAA + WFSFAA + EDBC 10/2012 add'l)
    # ============================================================
    dict(fid="sfaa_residency_eligibility",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="general", url=f"{SFAA_URL}#page=2",
         text="持學生簽證的小朋友可以申請書簿津貼嗎？《SFAA Guidance Notes 2025/26》§1.1.1（註）："
              "The student-applicants must be unmarried Hong Kong Residents, with right of abode, right to land or valid permission to remain without any condition of stay (other than the limit of stay) in Hong Kong. Students holding visitor visas, two-way exit permits, student visas only or who are dependents of student-visa / visitor-visa holders are not eligible to apply for student financial assistance",
         keywords=["SFAA", "WFSFAA", "Hong Kong Resident", "right of abode",
                   "居港權", "student visa", "學生簽證", "visitor visa",
                   "two-way exit permit", "雙程證", "ineligible",
                   "不合資格", "residency"],
         q="持學生簽證的小朋友可以申請書簿津貼嗎"),

    dict(fid="sfaa_afi_formula",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="general", url=f"{SFAA_URL}#page=3",
         text="調整後家庭入息點計？單親家庭點處理？《SFAA Guidance Notes 2025/26》§§3.1-3.2（註）："
              "The SFO will use the \"Adjusted Family Income\" (AFI) mechanism as the means test to assess the eligibility of a family for student financial assistance and its assistance level. … AFI = Gross annual income of the family / (Number of family members + (1)) … For single-parent families of 2 to 3 members, the \"plus 1 factor\" in the divisor of AFI formula will be increased to 2.",
         keywords=["AFI", "Adjusted Family Income", "調整後家庭入息",
                   "means test", "入息審查", "single-parent", "單親",
                   "plus 1 factor", "SFO", "SFAA"],
         q="調整後家庭入息點計 AFI 單親"),

    dict(fid="sfaa_afi_primarysec_2024_25",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="general", url=f"{SFAA_URL}#page=3",
         text="中小學書簿津貼入息限額 全額／半額？《SFAA Guidance Notes 2025/26》§3.3.1（註）："
              "Applicable to Financial Assistance Schemes for Primary and Secondary Students — 2024/25 school year - AFI Groups (HK$) (for reference only): 0–44,495 Full*; 44,496–86,039 Half; > 86,039 Ineligible (applications not successful). … * AFI thresholds for full level of assistance for 3-member and 4-member families are $53,868 and $49,559 respectively in the 2024/25 school year. For 2-member single-parent families and 3-member single-parent families, they are regarded as 3-member families and 4-member families respectively for determining the AFI thresholds for full level of assistance and calculation of AFI.",
         keywords=["AFI", "中小學", "primary", "secondary", "44,495",
                   "86,039", "53,868", "49,559", "Full", "Half",
                   "全額", "半額", "2024/25", "SFAA"],
         q="中小學書簿津貼 入息限額 全額 半額"),

    dict(fid="sfaa_kg_3tier_afi",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="kindergarten", url=f"{SFAA_URL}#page=3",
         text="幼稚園學費減免 三級 入息分層？《SFAA Guidance Notes 2025/26》§3.3.2（註）："
              "Applicable to Financial Assistance Schemes for Pre-primary Students — 2024/25 school year - AFI Groups (HK$) (for reference only): 0–44,495 Full (100%)*; 44,496–54,505 3/4 (75%); 54,506–86,039 Half (50%); > 86,039 Ineligible (applications not successful).",
         keywords=["KCFR", "幼稚園", "kindergarten", "pre-primary",
                   "AFI", "44,495", "54,505", "86,039", "100%", "75%", "50%",
                   "Full", "3/4", "Half", "2024/25"],
         q="幼稚園學費減免 全額 四分三 半額"),

    dict(fid="sfaa_full_day_social_needs",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="kindergarten", url=f"{SFAA_URL}#page=4",
         text="全日制幼兒中心要做社會需要測試？半日制呢？《SFAA Guidance Notes 2025/26》§3.5（註）："
              "\"Social needs\" test (for application with children aged between 0 and 3 attending whole-day child care centre or kindergarten-cum-child care centre) — Applicants with children receiving whole-day child care services (i.e. groups aged 0 to 2 and 2 to 3) must pass the AFI means test and the \"social needs\" test within the same assessment period in order to qualify themselves for the fee remission. Therefore, applicants should complete the \"Social Needs\" Assessment Form for Kindergarten and Child Care Centre Fee Remission (SFO 235A) in addition to the application form … Those receiving half-day child care services are not eligible to apply for KCFR Scheme.",
         keywords=["social needs test", "社會需要測試", "全日制", "whole-day",
                   "child care centre", "幼兒中心", "0-3", "SFO 235A",
                   "KCFR", "half-day", "半日制", "不合資格"],
         q="全日制 child care 社會需要測試"),

    dict(fid="sfaa_kcfr_deadline_15aug",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="kindergarten", url=f"{SFAA_URL}#page=6",
         text="幼稚園學費減免申請截止日期係幾時？《SFAA Guidance Notes 2025/26》§4.6 table（註）："
              "Kindergarten and Child Care Centre Fee Remission (KCFR) Scheme — Applicants should forward their \"Household Application Form for Student Financial Assistance Schemes\" to the SFO before the completion of attending classes in the 2025/26 school year or not later than 15 August 2026, whichever is the earlier. Otherwise, fee remission will generally not be released even if they can pass the means test and meet the eligibility criteria. The effective month of fee remission will be the month in which the application forms are submitted by the applicants, or the month in which the student-applicants are admitted to the kindergartens / child care centres, whichever is the later.",
         keywords=["KCFR", "幼稚園學費減免", "15 August 2026", "15 Aug",
                   "deadline", "截止", "申請", "effective month", "生效月份",
                   "SFAA", "child care centre", "2025/26"],
         q="幼稚園學費減免 申請截止日期"),

    dict(fid="sfaa_ta_deadline_31oct",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="general", url=f"{SFAA_URL}#page=6",
         text="書簿津貼申請截止日期係幾時？《SFAA Guidance Notes 2025/26》§4.6 table（註）："
              "School Textbook Assistance (TA) Scheme — Applicants should submit their \"Household Application Form for Student Financial Assistance Schemes\" to the SFO on or before 31 October 2025. Otherwise, School Textbook Assistance will generally not be released even if they can pass the means test and meet the eligibility criteria.",
         keywords=["TA", "School Textbook Assistance", "書簿津貼",
                   "31 October 2025", "31 Oct", "10月31日", "deadline",
                   "截止", "SFAA", "申請", "means test"],
         q="書簿津貼 申請截止日"),

    dict(fid="sfaa_ec_school_role",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="general", url=f"{SFAA_URL}#page=5",
         text="Eligibility Certificate 學校點處理？有期限嗎？《SFAA Guidance Notes 2025/26》§4.1.1 table September 2025 row（註）："
              "Applicants receiving ECs must verify carefully the personal information and selected Scheme(s) pre-filled on the ECs. Applicants should return the completed ECs to the school in which the children are attending within one week after the commencement date of the school or within two weeks from the issue date of ECs (whichever is the later) for processing. Schools will certify the student-applicants' status and attendance and then forward the ECs to the SFO. In general, the SFO will not accept any ECs submitted after the deadline.",
         keywords=["EC", "Eligibility Certificate", "資格證明書",
                   "one week", "兩星期", "school certify", "核證",
                   "SFO", "SFAA", "forward", "轉交", "deadline"],
         q="Eligibility Certificate 學校點處理 期限"),

    dict(fid="sfaa_kg_payment_flow",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="kindergarten", url=f"{SFAA_URL}#page=7",
         text="幼稚園學費減免點樣發放畀家長？《SFAA Guidance Notes 2025/26》§6.2（註）："
              "For Kindergarten and Child Care Centre Fee Remission, the approved amount of fee remission will be paid to the kindergartens / child care centres concerned directly by the Treasury in about 10 working days after the issue of notification of result with fee remission amount. Payment to applicants will then be arranged by the kindergartens / child care centres.",
         keywords=["KCFR", "Treasury", "庫務署", "kindergarten",
                   "幼稚園", "10 working days", "10個工作天",
                   "payment to applicants", "幼稚園發放", "child care centre"],
         q="幼稚園學費減免 點樣發放畀家長"),

    dict(fid="sfaa_overpayment_suspend",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="general", url=f"{SFAA_URL}#page=7",
         text="書簿津貼會被暫停或追回嗎？《SFAA Guidance Notes 2025/26》§6.6（註）："
              "Notwithstanding paragraphs 6.1 to 6.3 above, the WFSFAA may at any time withhold or suspend / cease the payment of financial assistance or loan to eligible applicants … if: (i) any irregularity in any of the applicant's applications … is detected (including but not limited to applications with incomplete information provided or information which is suspected to be false) during the vetting / counter-checking / reviewing processes; (ii) the applicant fails to provide the complete information as required … (iii) the WFSFAA has ground to believe that there has been overpayment(s) to an applicant, or that any amount was due to be paid by the applicant to the Government …",
         keywords=["WFSFAA", "suspend", "cease", "暫停", "終止",
                   "withhold", "irregularity", "false information",
                   "虛假資料", "overpayment", "過額", "退款"],
         q="書簿津貼 暫停 追回 條件"),

    dict(fid="sfaa_doc_retain_2yr",
         source_id="wfsfaa_sfaa_household_app_guidance_2526",
         title="SFAA Household Application Guidance Notes 2025/26",
         topic="general", url=f"{SFAA_URL}#page=7",
         text="申請津貼嘅證明文件要保留幾耐？《SFAA Guidance Notes 2025/26》§5.5（註）："
              "It is the responsibility of applicants to keep all supporting documents of the application data for at least two years, and they should cooperate with the WFSFAA staff. Intentional obstruction to the WFSFAA staff in their course of verification, concealment of facts or failure to provide the information required will lead to restitution in full of the assistance granted (including the financial assistance granted under all financial assistance scheme(s) administered by the WFSFAA) and possible prosecution.",
         keywords=["supporting documents", "證明文件", "2 years", "兩年",
                   "concealment", "隱瞞", "obstruction", "阻撓",
                   "WFSFAA", "prosecution", "刑事檢控", "restitution"],
         q="津貼 證明文件 要保留幾耐"),

    dict(fid="tas_afi_2024_25_rates",
         source_id="wfsfaa_primarysec_amount_2526",
         title="WFSFAA Amount of Financial Assistance 2025/26",
         topic="general", url=WFSFAA_AMOUNT_URL,
         text="2025/26 書簿津貼金額係幾多？《WFSFAA Amount of Financial Assistance 2025/26》（註）："
              "School Textbook Assistance (TA) 2025/26 — Full Grant rates: Primary 1-6: $6,206; S1-S3: $6,338; S4: $6,328; S5: $5,744; S6: $3,634. Half Grant rates: Primary 1-6: $3,103; S1-S3: $3,169; S4: $3,164; S5: $2,872; S6: $1,817.",
         keywords=["TA", "School Textbook Assistance", "書簿津貼", "2025/26",
                   "Full Grant", "Half Grant", "全額", "半額",
                   "6,206", "6,338", "6,328", "5,744", "3,634",
                   "3,103", "3,169", "P1-6", "S1-S3"],
         q="2025/26 書簿津貼 金額 中一"),

    dict(fid="sia_grant_household_2025_26",
         source_id="wfsfaa_primarysec_amount_2526",
         title="WFSFAA Amount of Financial Assistance 2025/26",
         topic="general", url=WFSFAA_AMOUNT_URL,
         text="2025/26 上網費資助每戶金額？《WFSFAA Amount of Financial Assistance 2025/26》（註）："
              "Full rate of subsidy for SIA in the 2025/26 school year is $1,700 per household while the half rate is $850 per household.",
         keywords=["SIA", "上網費資助", "Internet Access Subsidy",
                   "1,700", "850", "per household", "每戶",
                   "Full rate", "Half rate", "2025/26"],
         q="上網費資助 幾錢 一年"),

    dict(fid="edbc10_2012_smc_imc_transparency",
         source_id="edbc_10_2012_fee_remission",
         title="EDBC 10/2012 Fee Remission/Scholarship Schemes in DSS Schools",
         topic="general", url=f"{EDBC10_2012_URL}#page=2",
         text="DSS 學校學費減免 學校責任 開學前要處理？《EDBC 10/2012》§5(a),(b),(d),(f)（註）："
              "DSS schools are required to consult their School Management Committee (SMC)/Incorporated Management Committee (IMC) or parent-teacher associations on the operation of their school fee remission/scholarship schemes … DSS schools are required to clearly indicate in the application form for admission and the School Profile … that needy students, including those from families receiving the CSSA and students receiving financial assistance provided by the Student Finance Assistance Agency (SFAA), could apply for school fee remission. … subject to the availability of funds under the school fee remission/scholarship schemes, in principle, DSS schools are required to offer fee remission to students from families receiving the CSSA and those receiving assistance from the SFAA. … DSS schools should as far as possible complete processing the applications for school fee remission schemes from newly admitted students before the new school year begins so that those eligible students will not be required to pay the school fee in advance.",
         keywords=["DSS", "EDBC 10/2012", "SMC", "IMC", "校管會", "法團校董會",
                   "School Profile", "CSSA", "SFAA", "needy students",
                   "before new school year", "開學前", "新生申請"],
         q="DSS 學費減免 學校責任 開學前"),

    dict(fid="edbc10_2012_reserve_excess",
         source_id="edbc_10_2012_fee_remission",
         title="EDBC 10/2012 Fee Remission/Scholarship Schemes in DSS Schools",
         topic="general", url=f"{EDBC10_2012_URL}#page=3",
         text="DSS fee remission reserve 過剩 點處理？《EDBC 10/2012》§6（4 acceptable options）（註）："
              "Currently, when the reserve for the fee remission/scholarship scheme of a DSS school has reached a cumulative amount that exceeds the school's half-year total fee income due to low utilisation of the scheme, the SMC/IMC should devise a plan on how this specific reserve could be effectively deployed and submit it to the EDB for consideration. Acceptable options to avoid excessive reserve include: (a) relaxing the criteria for awarding fee remission/scholarship; (b) reducing the school fees; (c) subsidizing eligible students in their purchase of textbooks/reference books/stationery; and (d) sponsoring eligible students for joining extra-curricular activities, such as overseas educational visits and exchange study programmes, etc.",
         keywords=["DSS", "EDBC 10/2012", "fee remission reserve",
                   "減免儲備", "half-year fee income", "半年學費收入",
                   "4 options", "relaxing criteria", "reducing school fees",
                   "exchange study", "ECA"],
         q="DSS fee remission reserve 過多 4個選項"),

    dict(fid="edbc10_2012_exemption_3yr",
         source_id="edbc_10_2012_fee_remission",
         title="EDBC 10/2012 Fee Remission/Scholarship Schemes in DSS Schools",
         topic="general", url=f"{EDBC10_2012_URL}#page=4",
         text="DSS 可申請豁免「不遜於政府資助」基線嗎？條件？《EDBC 10/2012》§8（註）："
              "DSS schools meeting the following criteria be allowed to apply to the EDB for exemption from the requirement for DSS schools to adopt eligibility criteria for fee remission schemes no less favourable than those of the government financial assistance schemes: (a) the utilization rates of their fee remission/scholarship provisions are 100% or more as reflected in the audited accounts of the past three consecutive years; and (b) in overall terms, during the three years in question, two thirds of their fee remission/scholarship provisions or more have been used for fee remission purposes as confirmed by the schools.",
         keywords=["DSS", "EDBC 10/2012", "exemption", "豁免",
                   "no less favourable", "不遜於", "utilization 100%",
                   "3 consecutive years", "3年", "two thirds", "三分之二"],
         q="DSS fee remission exemption 申請條件"),

    dict(fid="edbc10_2012_through_train_50",
         source_id="edbc_10_2012_fee_remission",
         title="EDBC 10/2012 Fee Remission/Scholarship Schemes in DSS Schools",
         topic="general", url=f"{EDBC10_2012_URL}#page=5",
         text="一條龍直資中小學 學費減免儲備可以轉移嗎？《EDBC 10/2012》§13（註）："
              "To facilitate better utilization of fee remission/scholarship reserves in through-train secondary and primary schools, thereby enabling them to admit more needy students overall, the Working Group has recommended that through-train secondary and primary schools be allowed to transfer a maximum of 50% of the fee remission/scholarship reserves of the linked primary school to the linked secondary school or vice versa should they meet the following conditions and obtain prior approval from their SMC/IMC: (a) the utilization rates of the fee remission/scholarship provisions of the linked school which is to receive funds are 100% or more as reflected in the audited accounts of the past three consecutive years; and (b) in the past three years, two thirds of the fee remission/scholarship provisions or more of the linked school which is to receive funds are used for fee remission purposes as confirmed by the schools.",
         keywords=["DSS", "EDBC 10/2012", "through-train", "一條龍",
                   "transfer 50%", "轉移", "linked primary", "linked secondary",
                   "fee remission reserves", "SMC", "IMC", "3 years",
                   "two thirds"],
         q="一條龍 直資 學費減免儲備 轉移"),

    # ============================================================
    # Angle 06 — NET Scheme (EDBC 8/2025 + Point-to-note + package + fringe benefits)
    # ============================================================
    dict(fid="net_2025_two_option",
         source_id="edbc_8_2025_net_enhancement",
         title="EDBC 8/2025 Enhancement Measures for the NET Scheme",
         topic="general", url=f"{EDBC8_2025_NET_URL}#page=1",
         text="NET 計劃 2025/26 改革：學校可以選擇咩？《EDBC 8/2025》§3（註）："
              "Starting from the 2025/26 school year, eligible aided schools (including special schools) and caput schools can opt for either (i) retaining the existing NET post; or (ii) receiving a new NET Grant when the current contracts with NETs or service providers are completed.  The enhanced arrangement will enable schools to tailor their manpower resources to better meet their students' needs.  Schools should adopt a holistic approach based on their school-based circumstances to make prudent decisions when opting for retaining a NET post or receiving the NET Grant.",
         keywords=["NET", "外籍英語教師", "EDBC 8/2025", "2025/26",
                   "two-option", "retain NET post", "NET Grant",
                   "aided schools", "caput schools", "service provider"],
         q="NET 計劃 2025/26 改革 兩個選擇"),

    dict(fid="net_grant_900k_1m",
         source_id="edbc_8_2025_net_enhancement",
         title="EDBC 8/2025 Enhancement Measures for the NET Scheme",
         topic="general", url=f"{EDBC8_2025_NET_URL}#page=3",
         text="NET Grant 金額幾多？幾時派？《EDBC 8/2025》§12（註）："
              "The NET Grant is a purpose-specific grant disbursed to eligible schools every school year, with an ambit aligned with the objectives of the NET Scheme.  The amount of the NET Grant is referenced to the mid-point salary of Assistant Primary School Master/Mistress (APSM) in aided primary schools, and the mid-point salary of Graduate Master/Mistress (GM) in aided secondary schools.  The full year amount of the NET Grant for eligible primary and secondary schools are $900,000 and $1,000,000 respectively annually.  The NET Grant will be disbursed to aided schools (including special schools) by two instalments in September and April every school year.",
         keywords=["NET Grant", "900,000", "1,000,000",
                   "primary", "secondary", "中學", "小學",
                   "APSM", "GM", "mid-point salary",
                   "September", "April", "two instalments", "EDBC 8/2025"],
         q="NET Grant 金額幾多 中學 小學"),

    dict(fid="net_gratuity_10_15",
         source_id="edbc_8_2025_net_enhancement",
         title="EDBC 8/2025 Enhancement Measures for the NET Scheme",
         topic="general", url=f"{EDBC8_2025_NET_URL}#page=3",
         text="新入職 NET 約滿酬金比率係幾多？《EDBC 8/2025》footnote 1（註）："
              "For NETs serving in the 1st and 2nd contracts: 10% of total current basic salary (when added to the employer's contribution to the Mandatory Provident Fund Scheme) paid over the contract period payable on satisfactory completion of each contract; For NETs serving after 2 contracts: 15% of total current basic salary (when added to the employer's contribution to the Mandatory Provident Fund Scheme) paid over the contract period payable on satisfactory completion of each contract and upon fulfilling training requirements for newly-joined teachers within first three years of services.",
         keywords=["NET", "contract gratuity", "約滿酬金", "10%", "15%",
                   "1st contract", "2nd contract", "MPF",
                   "強積金", "newly-joined", "training requirements",
                   "EDBC 8/2025"],
         q="新入職 NET gratuity 比率 10% 15%"),

    dict(fid="net_grant_min_1nat",
         source_id="edb_point_to_note_net_grant_202627",
         title="Point-to-note for Receiving NET Grant 2026/27",
         topic="general", url=f"{NET_GRANT_NOTE_URL}#page=1",
         text="收 NET Grant 嘅學校要請幾多人？《Point-to-note for Receiving NET Grant 2026/27》§2（註）："
              "Schools receiving the NET Grant should employ at least one full-time NET for the school year.  If there are remaining funds, schools can employ native-speaking English Teaching Assistants (NTAs) and/or engage English learning support services provided by proficient speakers of English.",
         keywords=["NET Grant", "full-time NET", "全職 NET",
                   "at least one", "最少一位", "NTA", "Teaching Assistant",
                   "外籍英語教學助理", "English learning support",
                   "2026/27"],
         q="NET Grant 學校要請幾多人"),

    dict(fid="net_qual_ielts_75",
         source_id="edb_point_to_note_net_grant_202627",
         title="Point-to-note for Receiving NET Grant 2026/27",
         topic="general", url=f"{NET_GRANT_NOTE_URL}#page=3",
         text="NET 入職資格係咩？IELTS 要幾分？《Point-to-note for Receiving NET Grant 2026/27》Annex 1（註）："
              "The applicant should be a native-speaker of English or possess native-speaker English competence.  The applicant should obtain the following qualifications: (i) a Bachelor's degree in any subject from a Hong Kong university, or equivalent; and (ii) A Post-graduate Diploma in Education (PGDE) or a Teaching English as a Foreign / Second Language (TEFL / TESL) qualification at certificate level, or equivalent; and (iii) valid IELTS results (overall band score of 7.5 or above, with \"Speaking\" band score of 7.5 or above)",
         keywords=["NET", "IELTS", "7.5", "Speaking 7.5",
                   "native-speaker", "外籍", "Bachelor", "學士",
                   "PGDE", "TEFL", "TESL", "qualifications", "入職資格"],
         q="NET 入職資格 IELTS 7.5"),

    dict(fid="net_surplus_30pct",
         source_id="edb_point_to_note_net_grant_202627",
         title="Point-to-note for Receiving NET Grant 2026/27",
         topic="general", url=f"{NET_GRANT_NOTE_URL}#page=2",
         text="NET Grant 剩餘款項點處理？30% 上限？《Point-to-note for Receiving NET Grant 2026/27》§7（註）："
              "For aided schools (including special schools), based on schools' annual audited account, if schools have accumulated a surplus in excess of 30% of the 12 months' provision of the NET Grant, the surplus above this amount at the end of the school year will be clawed back.  Transfer of funds/unspent balance out of the NET Grant is not allowed.",
         keywords=["NET Grant", "surplus", "結餘", "30%",
                   "12 months provision", "claw back", "追回",
                   "audited annual account", "transfer not allowed", "aided schools"],
         q="NET Grant 剩餘款項 30% 上限"),

    dict(fid="net_grant_school_plan",
         source_id="edb_point_to_note_net_grant_202627",
         title="Point-to-note for Receiving NET Grant 2026/27",
         topic="general", url=f"{NET_GRANT_NOTE_URL}#page=2",
         text="NET Grant School Plan / School Report 要點？《Point-to-note for Receiving NET Grant 2026/27》§8（註）："
              "To ensure the proper use of the NET Grant, schools receiving the Grant should submit an annual School Plan and School Report on the deployment of the Grant for endorsement by their Incorporated Management Committees (IMCs) / School Management Committees (SMCs) each school year, summarising the implementation and evaluating the effectiveness of relevant measures in supporting English learning, and upload them onto the school homepage for the sake of enhancing transparency and in accordance with the established practice.",
         keywords=["NET Grant", "School Plan", "School Report",
                   "IMC", "SMC", "endorsement", "通過",
                   "school homepage", "學校網頁", "transparency", "透明度",
                   "annual"],
         q="NET Grant School Plan School Report 要點"),

    dict(fid="net_mps_salary",
         source_id="edb_net_package_pdf",
         title="Remuneration Package for NETs (EDB summary PDF)",
         topic="general", url=f"{NET_PACKAGE_URL}#page=1",
         text="NET 薪酬範圍係幾多？APSM GM 點計？《Remuneration Package for NETs》(a) Monthly Salary（註）："
              "For Primary NETs: (a) Assistant Primary School Master/Mistress rank — The salary scale is from Master Pay Scale (MPS) Point 15 (HK$24,450 per month) to MPS Point 29 (HK$47,290 per month); (b) Certificated Master/Mistress rank — The salary scale is from MPS Point 14 (HK$23,285 per month) to MPS Point 24 (HK$37,625 per month). For Secondary NETs: (a) Graduate Master/Mistress rank — The salary scale is from MPS Point 15 (HK$24,450 per month) to MPS Point 33 ($56,810 per month).",
         keywords=["NET", "salary", "薪酬", "APSM", "GM",
                   "Assistant Primary School Master", "Graduate Master",
                   "Certificated Master", "MPS", "Master Pay Scale",
                   "24,450", "47,290", "23,285", "37,625", "56,810"],
         q="NET 薪酬 APSM GM"),

    dict(fid="net_special_allowance_16859",
         source_id="edb_net_package_pdf",
         title="Remuneration Package for NETs (EDB summary PDF)",
         topic="general", url=f"{NET_PACKAGE_URL}#page=2",
         text="NET special allowance（住屋津貼）幾多？《Remuneration Package for NETs》(f)（註）："
              "Special allowance — A fixed monthly allowance currently fixed at HK$16,859.  (A NET will not be eligible for the special allowance if he/she or his/her spouse is already receiving the same or housing allowance from his/her own employer.)",
         keywords=["NET", "special allowance", "特別津貼", "住屋津貼",
                   "16,859", "monthly", "每月",
                   "spouse", "housing allowance", "double benefit"],
         q="NET special allowance 住屋津貼幾多"),

    dict(fid="net_baggage_allowance",
         source_id="edb_net_package_pdf",
         title="Remuneration Package for NETs (EDB summary PDF)",
         topic="general", url=f"{NET_PACKAGE_URL}#page=1",
         text="NET baggage allowance 行李津貼？《Remuneration Package for NETs》(e)（註）："
              "Baggage allowance — Reimbursement of travelling baggage expenses from and to the country of origin will be provided.  The present rates are: Outward passage (on first appointment only) — Single: HK$1,300; Married (accompanied by spouse and/or children): HK$5,000.  Homebound passage (after finishing a contract and will not be in the Schemes in the current/coming school year) — Single: HK$3,300; Married (accompanied by spouse and/or children): HK$6,500.",
         keywords=["NET", "baggage allowance", "行李津貼",
                   "Outward", "Homebound", "Single", "Married",
                   "1,300", "5,000", "3,300", "6,500",
                   "spouse", "children", "country of origin"],
         q="NET baggage allowance 行李津貼"),

    dict(fid="net_medical_allowance",
         source_id="edb_net_package_pdf",
         title="Remuneration Package for NETs (EDB summary PDF)",
         topic="general", url=f"{NET_PACKAGE_URL}#page=2",
         text="NET medical insurance 補助上限？《Remuneration Package for NETs》(g)（註）："
              "Medical allowance — As reimbursement for the appointees to undertake medical insurance, up to HK$1,400 per year for single appointee and $5,400 per year for married appointee accompanied by spouse and/or children.",
         keywords=["NET", "medical allowance", "醫療津貼", "醫療保險",
                   "1,400", "5,400", "per year",
                   "single", "married", "spouse", "reimbursement"],
         q="NET medical insurance reimbursement 上限"),

    dict(fid="net_passage_5persons",
         source_id="edb_net_package_pdf",
         title="Remuneration Package for NETs (EDB summary PDF)",
         topic="general", url=f"{NET_PACKAGE_URL}#page=1",
         text="NET 機票補助 範圍係咩？《Remuneration Package for NETs》(d)（註）："
              "Passage — Reimbursement of expenses on standard economy air tickets from and to the country of origin by the most direct route for the appointee, his/her spouse and accompanying children, up to 5 persons including the teacher, for each contract.",
         keywords=["NET", "passage", "機票補助", "air tickets",
                   "economy", "經濟艙", "most direct route", "5 persons",
                   "5人", "spouse", "children", "per contract"],
         q="NET 機票補助 範圍"),

    dict(fid="net_overseas_residence_gate",
         source_id="edbc_8_2009_fringe_benefits",
         title="EDBC 8/2009 NET Scheme in Primary Schools: Fringe Benefits",
         topic="general", url=f"{EDBC8_2009_URL}#page=1",
         text="NET 海外居住身份津貼資格係點？《EDBC 8/2009》§2（註）："
              "NETs are entitled to passages, baggage allowance, special allowance and medical allowance provided under the NET Scheme in Primary Schools only if their normal place of residence is outside Hong Kong. For a NET to establish that his/her normal place of residence is outside Hong Kong, he/she should satisfy the following criteria: (a) possessing permanent resident status in a country/place outside Hong Kong; and (b) his/her social ties being outside Hong Kong.",
         keywords=["NET", "fringe benefits", "normal place of residence",
                   "海外居住", "permanent resident", "永久居民",
                   "social ties", "outside Hong Kong",
                   "PNET", "EDBC 8/2009", "eligibility"],
         q="NET 海外居住身份 津貼資格"),

    dict(fid="net_double_benefit",
         source_id="edbc_8_2009_fringe_benefits",
         title="EDBC 8/2009 NET Scheme in Primary Schools: Fringe Benefits",
         topic="general", url=f"{EDBC8_2009_URL}#page=2",
         text="NET 重複津貼點處理？《EDBC 8/2009》§5（註）："
              "When certifying the eligibility of a NET for the fringe benefits, schools should note that the NET is required to declare that he/she or his/her spouse is not receiving any similar benefits. A NET will not be eligible for the Special Allowance if he/she or his/her spouse is already receiving the same allowance or any other housing benefits from his/her own employer. Similarly, a NET will not be eligible for passages, baggage and medical allowance if he/she or his/her spouse is provided with similar benefits by his/her employer. All NETs receiving fringe benefits under the NET Scheme in Primary Schools should be required to report changes of marital status and family particulars, which may affect their entitlement, to the schools. Schools should then re-assess the NETs' eligibility for the fringe benefits.",
         keywords=["NET", "double benefits", "重複津貼",
                   "spouse", "similar benefits", "marital status",
                   "婚姻狀況", "re-assess", "重新評估",
                   "EDBC 8/2009", "declare"],
         q="NET 重複津貼"),

    dict(fid="net_apply_timeframes",
         source_id="edb_pnet_annex_jul2025",
         title="PNET Annex 23 Jul 2025 — Application time-frames",
         topic="general", url=PNET_ANNEX_URL,
         text="PNET 津貼／酬金 申請時間？《PNET Annex 23 Jul 2025》（註）："
              "Application for Special Allowance — August – September after commencement / prior to expiry of the Contract.  Application for Passage/Baggage Allowance — July – September of the respective school year (upon commencement of a contract / satisfactory completion of a contract).  Application for Medical Allowance — Before the end of the respective school year; Only one application should be submitted each school year.  Application for Retention Incentive (RI) — June – September of the respective school year.  Late application will not be considered.",
         keywords=["PNET", "Special Allowance", "Passage", "Baggage",
                   "Medical Allowance", "Retention Incentive", "RI",
                   "August", "September", "July", "June",
                   "申請時間", "late application", "23 Jul 2025"],
         q="PNET 津貼 申請時間"),

    dict(fid="net_imc_smc_oversight",
         source_id="edbc_8_2025_net_enhancement",
         title="EDBC 8/2025 Enhancement Measures for the NET Scheme",
         topic="general", url=f"{EDBC8_2025_NET_URL}#page=4",
         text="IMC／SMC 點監察 NET Grant？《EDBC 8/2025》§15（註）："
              "Incorporated Management Committees (IMCs) / School Management Committees (SMCs) should ensure that the resources are deployed in accordance with the ambit of the NET Grant and that each item of expenditure is utilised in a cost-effective manner in line with the principles of proper deployment of government funds.  Schools receiving the NET Grant should submit an annual School Plan and School Report on the deployment of the Grant for endorsement by their IMCs / SMCs each school year and upload them onto the school homepage for enhancing transparency.",
         keywords=["IMC", "SMC", "NET Grant", "deployment",
                   "ambit", "cost-effective", "school homepage",
                   "transparency", "School Plan", "School Report", "EDBC 8/2025"],
         q="IMC SMC NET 監察"),

    dict(fid="net_legacy_gratuity_15",
         source_id="edb_net_package_pdf",
         title="Remuneration Package for NETs (EDB summary PDF)",
         topic="general", url=f"{NET_PACKAGE_URL}#page=1",
         text="NET legacy contract gratuity 15%？《Remuneration Package for NETs》(c)（註）："
              "Contract gratuities — A sum together with employer's contribution to the Mandatory Provident Fund (MPF) Scheme that may equal to 15% of the total basic salary drawn during the contract period.",
         keywords=["NET", "contract gratuity", "約滿酬金", "15%",
                   "MPF", "強積金", "legacy",
                   "basic salary", "before 2025/26"],
         q="NET contract gratuity 15% legacy"),

    dict(fid="net_retention_incentive",
         source_id="edb_net_package_pdf",
         title="Remuneration Package for NETs (EDB summary PDF)",
         topic="general", url=f"{NET_PACKAGE_URL}#page=2",
         text="NET retention incentive 留任獎金幾耐先有？《Remuneration Package for NETs》(h)（註）："
              "Retention incentive — A cash retention incentive, 5% OR 10% of basic salary will be provided to eligible NETs serving in the third and fourth year OR the fifth year of continuous service onwards in Hong Kong respectively.  The incentive is not payable for the first two years of service.",
         keywords=["NET", "retention incentive", "留任獎金",
                   "5%", "10%", "third year", "fourth year",
                   "fifth year", "continuous service",
                   "not first two years", "newly-joined 2025/26"],
         q="NET retention incentive 留任獎金"),

    # ============================================================
    # Angle 07 — School Premises Safety + EMSD Lifts + Fire (idx 12/15/16 excluded)
    # ============================================================
    dict(fid="edbc12_2026_fire_annual",
         source_id="edbc_12_2026_fire_installations",
         title="教育局通告第12/2026號 校舍消防裝置或設備",
         topic="safety", url=f"{EDBC12_2026_URL}#page=1",
         text="校舍消防裝置幾耐要檢查一次？《教育局通告第12/2026號》§2 背景（註）："
              "作為維持校舍良好狀況的第一責任人，學校須遵守相關的消防安全要求。根據《教育規例》（第279A章）第39條，每間學校的校長須確保校舍內所有消防裝置或設備的性能時刻維持良好。此外，學校須遵守《消防(裝置及設備)規例》（第95B章）第8條，保持校舍內的消防裝置或設備時刻在有效操作狀態，及每12個月由一名註冊消防裝置承辦商(註冊消防承辦商)檢查有關消防裝置或設備至少一次(消防年檢)。如在任何時間包括於消防年檢中發現消防裝置或設備有任何損壞，學校必須立即處理，盡快使裝置或設備回復有效操作狀態。",
         keywords=["消防裝置", "消防設備", "FSI", "12個月", "消防年檢",
                   "Cap.279A §39", "Cap.95B §8", "第279A章", "第95B章",
                   "註冊消防承辦商", "校長責任", "EDBC 12/2026",
                   "fire service installation"],
         q="校舍消防裝置幾耐要檢查一次"),

    dict(fid="edbc12_2026_fs251_repair",
         source_id="edbc_12_2026_fire_installations",
         title="教育局通告第12/2026號 校舍消防裝置或設備",
         topic="safety", url=f"{EDBC12_2026_URL}#page=2",
         text="FS251 證書點申請緊急修葺？《教育局通告第12/2026號》§4（註）："
              "如利用緊急修葺工程機制維修於消防年檢中發現的損壞項目，申請時必須一併提供由註冊消防承辦商簽署的「消防裝置及設備證書」(FS251證書)。學校及其聘用負責消防年檢的註冊消防承辦商亦須與校舍保養管理組代表進行聯合視察，以確認有關損壞項目。",
         keywords=["FS251", "消防裝置及設備證書", "緊急修葺",
                   "註冊消防承辦商", "校舍保養管理組", "聯合視察",
                   "EDBC 12/2026", "Certificate of Fire Service Installations"],
         q="FS251 證書點申請緊急修葺"),

    dict(fid="edbc12_2026_fs251_display",
         source_id="edbc_12_2026_fire_installations",
         title="教育局通告第12/2026號 校舍消防裝置或設備",
         topic="safety", url=f"{EDBC12_2026_URL}#page=2",
         text="FS251 要唔要貼出嚟？《教育局通告第12/2026號》§5（註）："
              "當完成年檢後或維修損壞項目後，學校須從註冊消防承辦商處取得已簽署的FS251證書，並將證書張貼於校舍內的當眼處，以供消防處查核。",
         keywords=["FS251", "張貼", "當眼處", "消防處查核",
                   "fire service department", "certificate display",
                   "EDBC 12/2026"],
         q="FS251 要唔要貼出嚟"),

    dict(fid="edbc12_2026_24hr_notify",
         source_id="edbc_12_2026_fire_installations",
         title="教育局通告第12/2026號 校舍消防裝置或設備",
         topic="safety", url=f"{EDBC12_2026_URL}#page=2",
         text="消防裝置關閉幾時要通報教育局？《教育局通告第12/2026號》§6（註）："
              "如註冊消防承辦商向消防處發出「消防裝置關閉通知書」，學校必須於24小時內通知所屬的區域教育服務處及校舍保養管理組，並提供有關「消防裝置關閉通知書」的副本。當有關消防裝置恢復運作時，學校應透過註冊消防承辦商通知消防處，亦應同時通知所屬的區域教育服務處及校舍保養管理組。",
         keywords=["消防裝置關閉通知書", "24小時", "24-hour",
                   "區域教育服務處", "校舍保養管理組", "消防處",
                   "EDBC 12/2026", "FSI shutdown notice"],
         q="消防裝置關閉幾時要通報教育局 24小時"),

    dict(fid="edbc14_2024_cap279a_s5",
         source_id="edbc14_2024_spms",
         title="教育局通告第14/2024號 校舍巡察及保養",
         topic="safety", url=f"{EDBC14_2024_URL}#page=1",
         text="校舍保養係邊個負責？《教育局通告第14/2024號》§2 背景（註）："
              "根據《教育規例》（第279A章）第5條，學校須確保所有校舍無論何時均須維持令人滿意的修葺狀況。作為維持校舍良好狀況的第一責任人，學校有責任安排定時巡察校舍，並採取即時跟進行動，以確保校舍建築物（包括相關斜坡）保持良好狀況。",
         keywords=["校舍保養", "校舍巡察", "Cap.279A §5", "第279A章 第5條",
                   "第一責任人", "斜坡", "slope", "satisfactory state of repair",
                   "EDBC 14/2024", "premises maintenance"],
         q="校舍保養係邊個負責"),

    dict(fid="edbc14_2024_thresholds",
         source_id="edbc14_2024_spms",
         title="教育局通告第14/2024號 校舍巡察及保養",
         topic="safety", url=f"{EDBC14_2024_URL}#page=1",
         text="校舍維修申請邊個 fund？門檻點分？《教育局通告第14/2024號》§4（註）："
              "資助學校可適當運用政府提供的經常津貼為校舍進行小型修葺工程。至於規模較大及較複雜的修葺工程一般需要額外開支和專業知識，學校可向政府申請非經常津貼。資助學校應按照現行機制行事，具體如下：(a) 學校應適當運用相關經常津貼（例如營辦開支津貼或擴大的營辦開支整筆津貼中的學校及班級津貼）作日常保養及迅速推展小型修葺工程；及 (b) 學校可透過緊急修葺工程或大規模修葺工程，為每項費用達到或超過指定門檻的修葺項目申請非經常津貼。目前小學和特殊學校的門檻為3,000元，中學為8,000元，並將於2024/25學年分別調整至6,000元和10,000元。教育局會不時檢視及調整該門檻。",
         keywords=["校舍維修", "小型修葺", "緊急修葺", "大規模修葺",
                   "3,000元", "8,000元", "6,000元", "10,000元",
                   "經常津貼", "非經常津貼", "OEBG", "EDBC 14/2024"],
         q="校舍維修申請邊個 fund 門檻"),

    dict(fid="emsd_rp_definition",
         source_id="emsd_presentation_duties_rps",
         title="EMSD Presentation — 升降機及自動梯負責人簡介",
         topic="safety", url=f"{EMSD_RP_URL}#page=5",
         text="學校升降機邊個係 responsible person？《EMSD Presentation 升降機及自動梯負責人簡介》slide 5 §2 負責人的定義（註）："
              "升降機/自動梯負責人是指： 1. 升降機/自動梯的擁有人 (例如：業主、業主立案法團) 2. 任何其他對該升降機/自動梯有管理或控制權的人 (例如：物業管理公司) 註：如其中一名負責人遵從某規定，則其他負責人均被視為已遵從該規定",
         keywords=["升降機", "自動梯", "負責人", "RP", "responsible person",
                   "擁有人", "業主", "業主立案法團", "物業管理公司",
                   "Cap.618", "EMSD"],
         q="學校升降機邊個係 responsible person"),

    dict(fid="emsd_rp_duty_12_13",
         source_id="emsd_presentation_duties_rps",
         title="EMSD Presentation — 升降機及自動梯負責人簡介",
         topic="safety", url=f"{EMSD_RP_URL}#page=10",
         text="升降機負責人有咩責任？《EMSD Presentation 升降機及自動梯負責人簡介》slide 10 §4 負責人的責任 — 一（註）："
              "4. 負責人的責任：1. 確保升降機/自動梯及其所有相聯設備或機械保持於妥善維修狀況及安全操作狀態 (《條例》第12 & 44 條) 2. 確保升降機/自動梯在以下情況不被使用：當進行安裝、主要更改、拆卸、或可能影響安全操作的工程(《條例》第13 & 45 條(1))；並無有效的「准用證」(《條例》第13 & 45 條(2))；在進行主要更改工程後，沒有就該更改工程獲發「復用證」(《條例》第13 & 45 條(3))",
         keywords=["升降機", "lift", "responsible person", "負責人責任",
                   "Cap.618 §12", "§13", "§44", "§45",
                   "准用證", "復用證", "妥善維修", "EMSD"],
         q="升降機負責人有咩責任"),

    dict(fid="emsd_lift_annual_frequency",
         source_id="emsd_presentation_duties_rps",
         title="EMSD Presentation — 升降機及自動梯負責人簡介",
         topic="safety", url=f"{EMSD_RP_URL}#page=15",
         text="校舍升降機要幾耐檢一次？《EMSD Presentation 升降機及自動梯負責人簡介》slides 15-17 §4 負責人的責任 — 二至四（註）："
              "4. 負責人的責任：5. 確保註冊升降機/自動梯承辦商為升降機/自動梯進行保養工程，及每隔不超逾一個月進行定期保養工程(《條例》第15 & 46 條(2)) 6. 安排註冊升降機/自動梯工程師：a) 在升降機/自動梯投入使用及操作前，檢驗升降機/自動梯，及徹底檢驗所有相聯設備或機械 (《條例》第20 & 51 條) b) 在升降機/自動梯進行主要更改後，在恢復正常使用及操作前，徹底檢驗升降機/自動梯及其所有相聯設備或機械(《條例》第21 & 52 條) c) 在每隔不超逾12個月/6個月徹底檢驗該升降機/自動梯及其所有相聯設備或機械一次(定期檢驗)(《條例》第22 & 53 條) d) 在每隔不超逾5年，在負載的情況下，為升降機及其所有相聯設備或機械進行徹底檢驗一次(負載檢驗) (《條例》第23條)",
         keywords=["升降機", "自動梯", "每月", "每12個月", "5年",
                   "定期保養", "定期檢驗", "負載檢驗",
                   "Cap.618 §15", "§22", "§23", "§46", "§53",
                   "monthly maintenance", "annual inspection", "load test"],
         q="校舍升降機要幾耐檢一次"),

    dict(fid="emsd_use_permit_display",
         source_id="emsd_presentation_duties_rps",
         title="EMSD Presentation — 升降機及自動梯負責人簡介",
         topic="safety", url=f"{EMSD_RP_URL}#page=19",
         text="升降機准用證要貼邊度？《EMSD Presentation 升降機及自動梯負責人簡介》slide 19 §4（註）："
              "4. 負責人的責任：7. 確保有效的「准用證」時刻展示於升降機機廂內的顯眼位置，及自動梯的層站毗鄰的顯眼位置 (《條例》第39 & 69 條) 現有證明書有效期至下一次定期檢驗到期日",
         keywords=["准用證", "use permit", "升降機機廂",
                   "自動梯層站", "顯眼位置", "Cap.618 §39", "§69",
                   "下次定期檢驗", "EMSD"],
         q="升降機准用證要貼邊度"),

    dict(fid="emsd_serious_incident_24hr",
         source_id="emsd_presentation_duties_rps",
         title="EMSD Presentation — 升降機及自動梯負責人簡介",
         topic="safety", url=f"{EMSD_RP_URL}#page=22",
         text="升降機嚴重事故點通報？《EMSD Presentation 升降機及自動梯負責人簡介》slides 22-23 §4（註）："
              "4. 負責人的責任：8. 當知悉有嚴重的升降機/自動梯事故時，須在24小時內，以指明表格形式將該事故通知機電工程署及當時負責該升降機/自動梯的註冊承辦商(《條例》第40 & 70 條) 嚴重事故 (詳情見附表7)：有人死亡或受傷；主驅動系統發生故障；安全部件及安全設備發生故障；制動器發生故障；升降機的纜索斷裂；升降機的超載裝置發生故障；升降機的樓層門及機門的聯鎖裝置發生故障；自動梯的梯級鏈及驅動鏈發生故障",
         keywords=["嚴重事故", "serious incident", "24小時",
                   "機電工程署", "EMSD", "註冊承辦商",
                   "Cap.618 §40", "§70", "附表7", "Schedule 7"],
         q="升降機嚴重事故點通報 24小時"),

    dict(fid="emsd_penalty_table",
         source_id="emsd_presentation_duties_rps",
         title="EMSD Presentation — 升降機及自動梯負責人簡介",
         topic="safety", url=f"{EMSD_RP_URL}#page=32",
         text="升降機條例違規會罰幾錢？《EMSD Presentation 升降機及自動梯負責人簡介》slide 32 §5 罰則（註）："
              "5. 罰則 — 在沒有合理辯解之下，違反有關規定，可導致升降機/自動梯遭禁止使用和操作、罰款及監禁。第12、44條 — 最高罰款第五級(五萬元)；第13、45條 — 最高罰款第六級(十萬元)及監禁十二個月；第14條 — 最高罰款第六級(十萬元)及監禁十二個月；第15、46條(1) — 最高罰款第六級(十萬元)及監禁十二個月；第15、46條(2) — 最高罰款第五級(五萬元)；第20、21、22、23、51、52及53條 — 最高罰款第五級(五萬元)；第39、69條 — 最高罰款為第三級(一萬元)；第40、70條 — 最高罰款為第三級(一萬元)；第41、71條 — 最高罰款為第三級(一萬元)；一般規例 第2、17條 — 最高罰款為第三級(一萬元)；第69條 — 最高罰款為第三級(一萬元)",
         keywords=["罰則", "penalty", "第三級", "第五級", "第六級",
                   "一萬元", "五萬元", "十萬元", "監禁12個月",
                   "Cap.618", "fine", "imprisonment"],
         q="升降機條例違規會罰幾錢"),

    dict(fid="emsd_landing_rp_oneliner",
         source_id="emsd_le_ordinance_landing_tc",
         title="EMSD Cap.618 升降機及自動梯條例 landing",
         topic="safety", url=EMSD_LE_URL,
         text="升降機負責人定義（EMSD 官方 one-liner）？《EMSD Cap.618 landing》RP duty summary（註）："
              "升降機/自動梯的擁有人及任何其他對升降機/自動梯有管理權或操控權的人士(如物業管理公司)均為升降機/自動梯的負責人，他們須確保升降機/自動梯保持於妥善維修狀況及安全操作狀態。",
         keywords=["升降機", "自動梯", "負責人", "RP", "擁有人",
                   "物業管理公司", "妥善維修", "Cap.618", "EMSD"],
         q="升降機負責人定義 EMSD"),

    dict(fid="aud_fsi_owner_duty_en",
         source_id="audit_e61_ch6_fsi_monitoring",
         title="Audit Report 61 Ch.6 FSI Monitoring",
         topic="safety", url=f"{AUD61_URL}#page=7",
         text="FSI annual inspection legal requirement (English)？《Audit Report 61 Ch.6》§2.3（註）："
              "Where any fire service installations or equipment (FSI) have been installed in any premises, the owner of those premises shall (a) keep such FSI in efficient working order at all times; and (b) have such FSI inspected by an FSI contractor at least once in every 12 months.",
         keywords=["FSI", "fire service installations", "owner duty",
                   "efficient working order", "12 months", "annual",
                   "FSI contractor", "Cap.95B §8", "Audit Report 61"],
         q="FSI annual inspection legal requirement"),

    dict(fid="aud_fs251_14day",
         source_id="audit_e61_ch6_fsi_monitoring",
         title="Audit Report 61 Ch.6 FSI Monitoring",
         topic="safety", url=f"{AUD61_URL}#page=7",
         text="邊個可以簽 FS251 證書？幾耐內要發？《Audit Report 61 Ch.6》§§2.4-2.5（註）："
              "The Fire Service (Installations and Equipment) Regulations also require that: (a) no FSI shall be installed, maintained, inspected or repaired in any premises by any person other than an FSI contractor; and (b) whenever an FSI contractor installs, maintains, inspects or repairs any FSI, he shall within 14 days after completion of the work issue to the person on whose instructions the work was undertaken a certificate and forward a copy thereof to the FSD. The FSD requires FSI contractors to prepare their certificates using a standard form named as Form FS251 Certificate of Fire Service Installations and Equipment (FS251).",
         keywords=["FS251", "FSI contractor", "14 days", "14日",
                   "Cap.95B", "Fire Service Installations and Equipment Regulations",
                   "FSD", "Form FS251", "Audit Report 61"],
         q="邊個可以簽 FS251 證書 14日"),

    # FIX idx=17: SPLIT into two entries
    dict(fid="edbc22_2024_checklist_framing",
         source_id="edbc22_2024_student_safety",
         title="EDBC 22/2024 Measures related to Student Safety and Health",
         topic="safety", url=f"{EDBC22_2024_URL}#page=1",
         text="EDB 點解推 Student Safety Health Checklist？《EDBC 22/2024》§2（註）："
              "EDB has all along been working closely with schools to provide students with a safe environment, facilitating their effective learning and healthy development. The school governance authority and school management, as the primary responsible parties for the school, are required to continuously refine the school management system, enhance the standard and effectiveness of school governance, as well as properly assign work so that school staff could responsibly perform their respective duties. Hence, EDB, with reference to the chapters and topics that are related to student safety and health in the SAG, compiled the \"Checklist of Student Safety and Health Measures\" to facilitate schools in discharging their duties for promoting students' safety and health management.",
         keywords=["EDBC 22/2024", "Student Safety", "Health Checklist",
                   "primary responsible parties", "第一責任人",
                   "school governance", "SAG", "Student Safety and Health Measures",
                   "Checklist origin"],
         q="EDB Student Safety Health Checklist 點解推"),

    dict(fid="edbc22_2024_checklist_30nov",
         source_id="edbc22_2024_student_safety",
         title="EDBC 22/2024 Measures related to Student Safety and Health",
         topic="safety", url=f"{EDBC22_2024_URL}#page=2",
         text="Student Safety Health Checklist 幾時要交？要 IMC 簽嗎？《EDBC 22/2024》§5（註）："
              "Starting from the 2024/25 school year, upon completion of the aforesaid review and follow-up actions, schools are required to submit the completed \"Checklist of Student Safety and Health Measures\", endorsed by the Incorporated Management Committee/ School Management Committee, to the respective School Development Section on or before 30 November every year for record and retention.",
         keywords=["Student Safety Health Checklist", "30 November",
                   "11月30日", "IMC", "SMC", "endorsed", "通過",
                   "School Development Section", "EDBC 22/2024", "2024/25"],
         q="Student Safety Health Checklist 30 November IMC"),

    # ============================================================
    # Angle 09 — SAG Appendix Deep Extract (idx=5 excluded — dup of footnote_fn_sag_receipt)
    # ============================================================
    dict(fid="sag_apx_dorm_3day_report",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=97",
         text="特殊學校宿舍部嚴重意外要幾日內報？《學校行政手冊》Ch3 附錄2（註）："
              "資助特殊學校宿舍部宿生嚴重／危及生命的意外報告［須在意外發生後的3個曆日（包括公眾假期）內把本報告提交予學校所屬地區的高級學校發展主任］",
         keywords=["特殊學校", "宿舍", "嚴重意外", "3個曆日",
                   "3 calendar days", "公眾假期", "高級學校發展主任",
                   "學校行政手冊", "附錄2", "宿生", "報告"],
         q="特殊學校 宿舍 意外 報告 幾日"),

    dict(fid="sag_apx_first_aid_kit_16items",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=100",
         text="急救箱必備物品有咩？《學校行政手冊》Ch3 附錄3（註）："
              "急救箱內應存放的急救物品建議清單：1.經消毒的生理鹽水或蒸餾水（清潔傷處用）2.酒精（清潔器具用）3.用後即棄膠手套（以避免徒手直接接觸傷患處或血液）4.外科用口罩 5.不同大小的消毒敷料／敷料包／紗布（獨立包裝）6.不同闊度的彈性繃帶 7.三角繃帶 8.棉棒、藥棉 9.不同尺碼的膠布 10.剪刀 11.鑷子 12.洗眼用的噴壺或眼杯 13.冷敷墊 14.電子體溫計 15.人工呼吸面膜（用後即棄）或人工呼吸袋裝面罩 16.緊急求助資料（例如鄰近救護站的聯絡電話號碼）。*建議額外設置用品：自動心臟復甦機（學校應考慮添置此急救器材，以加強保護學生和員工）",
         keywords=["急救箱", "first aid kit", "16項物品", "生理鹽水",
                   "酒精", "膠手套", "外科口罩", "繃帶", "三角繃帶",
                   "膠布", "剪刀", "鑷子", "體溫計", "AED",
                   "自動心臟復甦機", "學校行政手冊", "附錄3"],
         q="急救箱 物品 16項"),

    dict(fid="sag_apx_fees_fines_table",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=156",
         text="學校核准罰款／費用上限？學生證補領幾錢？《學校行政手冊》Ch6 附錄3（註）："
              "核准徵收的罰款／費用一覽表（由2025年9月1日起生效，日後或會作出調整）：1.入學考試費 75元；2.補領學生證 每張50元；3.補領畢業證書 每張35元；4.修業成績表（第二份副本）每張35元；5.儲物櫃按金 每名學生15元（於學生離校時退回）；6.嚴重損毀或遺失圖書館書冊的罰款 書冊的原價另加20%手續費；7.逾期交還圖書館書冊的罰款 按照公共圖書館訂定的罰款額；9.弄毀及損壞科學儀器 每項物品75元；10.弄毀科學儀器以外的其他學校公物 75元（如由個別學生負責）／150元（如由全班負責）；11.蓄意破壞學校公物 修理／補購該項目的全費；12.影印儲值卡 每張按金35元（餘額退回給學生）；13.非標準項目收費（見附錄4）每名學生每年470元",
         keywords=["核准罰款", "費用", "75元", "50元", "35元", "15元",
                   "150元", "470元", "20%手續費", "學生證", "畢業證書",
                   "儲物櫃按金", "圖書館書冊", "2025年9月1日",
                   "學校行政手冊", "附錄3"],
         q="學生證 補領 收費"),

    dict(fid="sag_apx_non_std_fee_7cond",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=157",
         text="非標準項目收費 7 個條件（毋須事先批准）？《學校行政手冊》Ch6 附錄4（註）："
              "徵收作特定用途的費用條件：如能符合以下條件，學校毋須事先徵得教育局常任秘書長批准：a.所徵收的款額在現時教育局常任秘書長設定的上限以內。b.學校就所建議的計劃事先諮詢家長（最好在學期初進行），並且得到他們的贊同。c.應發給全體家長一份獲同意的收費詳細資料，並且張貼在校內當眼處。d.家長如有經濟困難不會被逼繳交收費。e.於學年完結時發給全體家長一份財務報表，告知他們如何運用所收集的費用。f.保存獨立的分類帳，以記錄有關每項收費的收支情況，並且在教育局要求時給予查閱。g.於經審核的周年帳目內，夾附一份獨立的報表，顯示與該等收費有關的一切收支項目。",
         keywords=["非標準項目收費", "7條件", "毋須事先批准",
                   "諮詢家長", "經濟困難", "財務報表",
                   "獨立分類帳", "周年帳目", "學校行政手冊", "附錄4"],
         q="非標準收費 7條件"),

    dict(fid="sag_apx_scrc_contractor",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=160",
         text="承辦商性罪行定罪紀錄查核（SCRC）條款點寫？《學校行政手冊》Ch6 附錄6（註）："
              "性罪行定罪紀錄查核服務規格範本：承辦商須要求所屬僱員（a）在職位申請表格及／或其他有關文件申報曾否在香港或其他地方被裁定觸犯任何刑事罪行，並提供詳細資料；以及（b）向香港警務處申請進行性罪行定罪紀錄查核。承辦商須徵求僱員同意，把有關(a)、(b)兩項的資料交予〔學校名稱〕，以便上述學校考慮承辦商的準僱員是否適合擔任有關工作。附註：承辦商須把下列事項告知僱員：1.僱員必須提供所需資料；2.僱員拒絕披露所需資料或故意提供虛假資料及／或隱瞞任何重要資料，有關求職申請將不獲受理；3.〔學校名稱〕會根據有關僱員提供的資料，考慮他們是否適合擔任有關職位；4.僱員曾被裁定觸犯刑事罪行，不一定視為不適合擔任有關職位；5.僱員有權要求查閱及改正已提供的資料，他們須以書面形式向承辦商提出有關要求。",
         keywords=["性罪行定罪紀錄查核", "SCRC", "承辦商",
                   "contractor clause", "刑事罪行", "香港警務處",
                   "僱員同意", "服務規格範本", "學校行政手冊", "附錄6"],
         q="承辦商 性罪行 查核"),

    dict(fid="sag_apx_sick_leave_28_48_168",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=215",
         text="月薪教職員病假規則？28日／48日／168日？《學校行政手冊》Ch7 附錄9（註）："
              "資助學校員工可享有的假期 — 月薪教學及非教學人員病假：a.首年受聘時享有28天病假，其後每服務滿一年，可享有全年共48天病假；b.有薪病假最高可累積至168天；c.全職或兼職的月薪常額或臨時教師，享有同等的病假；d.在享有的整段有薪病假期內，可支取全薪；e.僱員的積存病假一旦用罄，可獲批無薪病假；f.病假最少以半天為放取的單位；g.僱員如申請病假超逾兩天，必須出示有效的醫生證明書；h.教學人員如中斷服務超逾一年，會喪失積存的病假（由2006年9月1日生效）；i.專責人員／實驗室技術員／學校行政主任如中斷服務超逾45天，會喪失積存的病假。",
         keywords=["病假", "sick leave", "28天", "48天", "168天",
                   "月薪教學人員", "月薪非教學人員", "全薪",
                   "醫生證明書", "半天", "中斷服務一年", "45天",
                   "學校行政手冊", "附錄9"],
         q="教師 病假 幾多日"),

    dict(fid="sag_apx_maternity_14_40_4",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=216",
         text="教職員產假14週 + 額外4週 + 40週服務資格門檻？《學校行政手冊》Ch7 附錄9（註）："
              "女性僱員產假：放取產假前如以連續性合約受聘，可享有以下安排：連續放假14個星期，包括確實分娩日當日在內；僱員如在預產期後分娩，則假期日數可獲延長，由預產期之後一天起計直至確實分娩當日為止；及因懷孕或分娩導致生病或喪失工作能力的僱員，可額外獲批不超逾4個星期的假期（教師／專責人員／實驗室技術員／學校行政主任的額外產假可以無薪假期方式批假，假期可長達6個月）。有薪產假以14個星期為限。符合以下資格的僱員才可享有有薪產假：以薪金津貼支薪的教師／專責人員／實驗室技術員／學校行政主任／非教學人員在緊接放取所訂定的產假前已在學校服務滿40個星期。",
         keywords=["產假", "maternity leave", "14個星期", "40個星期",
                   "4個星期", "額外", "預產期", "連續性合約",
                   "薪金津貼", "學校行政手冊", "附錄9"],
         q="產假 14週 40週"),

    dict(fid="sag_apx_leave_approval_matrix",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=221",
         text="教學人員各類假期由校長定校董會批核？批核權力分配係點？《學校行政手冊》Ch7 附錄10（註）："
              "批核員工假期的人員：教學人員 — 有薪病假、產假、肺病特別假期及工傷假期由校長批核；無薪病假、產假及肺病特別假期由校董會批核；事假（因緊急重要的私人事務放假，每學年最多可放取兩天有薪假期）由校長批核；有薪進修假期（如獲教育局常任秘書長挑選參加某項培訓課程，例如複修課程，即同時獲批有薪假期）由校董會批核；具有合理理由而放取最多14天的特別有薪假期，例如執行社會服務，代表香港出席國際活動／教育會議，以及參與輔助服務隊的訓練活動，由校董會批核；其他無薪假期由校董會批核（只適用於已設立法團校董會的學校）。所有僱員出庭擔任陪審員或證人者，均可享有有薪假期，由校長批核。校長放假，由校董會批核。",
         keywords=["假期批核", "假期審批", "邊個批", "批核權力", "校長批核", "校長批", "校董會批核", "校董會批",
                   "教學人員假期", "有薪病假", "無薪病假", "產假", "肺病特別假期", "工傷假期",
                   "事假", "緊急私事假", "進修假期", "特別有薪假期", "陪審員", "證人",
                   "校長放假", "學校行政手冊", "附錄10"],
         q="教學人員嘅病假 事假 進修假期 邊個批 校長定校董會批"),

    dict(fid="sag_apx_coi_10_examples",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=223",
         text="學校利益衝突有咩具體例子？《學校行政手冊》Ch7 附錄11（註）："
              "利益衝突是指學校人員的個人利益與學校利益有所衝突。個人利益包括人員本身及以下人士的財政上或私人利益：家人或親屬；私交友好；所屬團體、會社及協會；與其有個人或社交聯繫的其他人士；任何他曾受其恩惠或欠下人情的人。出現利益衝突例子採購方面：a.職員在一間公司擁有財務利益或與此公司關係密切，而該公司為學校的貨品供應商或服務承辦商；b.職員負責評審和甄選供應商／服務承辦商的工作，但其本人、配偶、家人、親屬或私交友好於其中一間參與競投的公司擁有財務利益。職員招聘方面：d.校長聘用其親屬或朋友在學校任職，其間沒有依循既定的招聘程序；e.職員的親屬或朋友申請學校職位，由職員擔任面試人員，並錄用該親屬或朋友。收生／學生表現評核方面：f.職員或其好友的子女或親屬申請入學，職員親自面試，並建議錄取該名申請人。資料保密方面：h.職員泄露與學校運作有關的機密資料（例如收生面試問題、維修計劃），以優待其友或親屬。其他方面：i.職員與家長建立業務關係，或替家長或學生擔任外間工作（例如私人補習），或為學校承辦商擔任兼職工作；j.職員將其物業出租或售予學校。",
         keywords=["利益衝突", "conflict of interest", "COI",
                   "採購", "招聘", "收生", "資料保密",
                   "供應商", "親屬", "面試", "私人補習",
                   "學校行政手冊", "附錄11"],
         q="利益衝突 例子"),

    dict(fid="sag_apx_teacher_misconduct_proc",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=225",
         text="教師行為不當辭職、刑事如何處理？《學校行政手冊》Ch7 附錄12（註）："
              "處理教師行為不當個案的參考要點：辭職絕非解決有關教師行為不當個案的辦法，這並不符合學生的利益。學校應防止有嚴重不當行為（尤其屬刑事性質）的教師利用辭職妨礙調查及隱瞞其行為不當的記錄。如被懷疑行為不當的教師沒有給予校方足夠通知期而提出辭職，他應繳付所欠日數的薪酬作為代通知金，而金額的上限為其一個月的薪酬。雖然按《資助則例》的規定，校董會有權豁免要求員工以薪金代替通知期，但校董會作有關決定時必須審慎考慮有關教師所給予的理由是否充分，否則不應豁免其代通知金。當學校發現懷疑教師行為不當個案可能引致刑事訴訟或調查，或教師涉及任何在進行中的刑事訴訟或調查，包括但不限於被警方逮捕或拘捕時，應迅速採取行動，收集相關資料以評估不當行為的嚴重性和性質。如所收集的資料顯示有關不當行為屬刑事性質，學校必須立即向警方／廉政公署舉報，因任何延誤舉報，均有可能危及學生安全。同時，學校亦應採取預防措施以免驚動被懷疑的教師。根據《強制舉報虐待兒童條例》（第650章），學校不得僅因教師就嚴重虐兒個案作出舉報，而斷定該人員違反任何專業操守或專業道德的守則。",
         keywords=["教師行為不當", "辭職", "代通知金",
                   "刑事訴訟", "警方", "廉政公署", "ICAC",
                   "強制舉報虐待兒童條例", "第650章", "舉報保護",
                   "學校行政手冊", "附錄12"],
         q="教師 行為不當 辭職"),

    dict(fid="sag_apx_staff_record_retention",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=213",
         text="員工檔案資料保存期 1 年 / 2 年 / 7 年？《學校行政手冊》Ch7 附錄8（註）："
              "員工受聘資料保存期：員工的個人資料、資歷及專業訓練證明書副本、以往服務證明書副本、薪金詳情、個人公積金戶口的年度報表、假期記錄、外間工作記錄、聘用合約或聘書、利益申報表（如適用）— 員工離職後一年。獲選申請人的申請表和有關文件 — 按適當情況存入員工的個人檔案。列入候補或落選名單的申請人的申請表和有關文件 — 遴選工作完成後一年，或任何申索／上訴／投訴決議後一年，以時間較後者為準。考績報告、前僱主或個人推薦書、其他個人工作表現的評估資料 — 員工離職後一年。僱員補償申索文件 — 不超過員工離職後7年，或任何申索／上訴／投訴決議後一年，以時間較後者為準。服務證明書或考績證書 — 不超過員工離職後7年。各遴選委員會就聘用／晉升工作提交的報告 — 不超過遴選工作完成後兩年，或任何申索／上訴／投訴決議後一年，以時間較後者為準。有關人員行為失當的調查報告 — 員工離職後一年或任何申索／上訴／投訴決議後一年。",
         keywords=["員工檔案", "保存期", "離職後一年", "離職後7年",
                   "遴選工作完成後兩年", "PDPO", "個人資料",
                   "考績報告", "僱員補償", "學校行政手冊", "附錄8"],
         q="員工 紀錄 保存 幾耐"),

    dict(fid="sag_apx_cash_300m_10k",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=247",
         text="校外運送現金保安要求？300米／HK$10,000？《學校行政手冊》Ch8 附錄2（註）："
              "運送現金時可採取的保安措施：1.運送現金的時間、護送人、運送人及運送車輛均應盡量每次不同。為免員工與匪徒勾結，洩露運款資料，有關的資料應於需要時才讓有關員工知悉。運送現金的消息只應透露給有需要知悉的人士知道。運款路徑應揀選最直接的路線，避免行經橫街窄巷。2.學校應指派體格強健且可靠的員工負責運款的工作。3.運款人員須特別留意下列情況的出現：a.停泊在運款車附近路旁內有乘客的車輛，或正停在運款車旁邊的車輛；b.在附近門口或櫥窗等地方留連的人，他們身上可能暗藏武器；c.附近的路口、橫巷或類似容易被人襲擊的出口。4.員工在盡力保護所運款項的同時，必須首先注意本身安全。5.運款時最好不要徒步往返，並且不應徒步行走超過三百米的距離；亦要避免行經橫巷和人群擠迫的地方。6.如運送的現金款項超過10,000元，學校應考慮聘用護衞押款公司押運。",
         keywords=["運送現金", "保安", "三百米", "300米",
                   "10,000元", "押款公司", "運款", "保安措施",
                   "學校行政手冊", "附錄2"],
         q="運送 現金 步行 300米"),

    dict(fid="sag_apx_bbq_hotpot_safety",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=256",
         text="校園燒烤／火鍋活動消防安全？6米／滅火器？《學校行政手冊》Ch8 附錄5（註）："
              "在學校舉辦燒烤及火鍋活動須知與消防安全建議 — 燒烤活動：a.燒烤活動只可於上課以外的時間進行；b.燒烤場地應處於空曠而又不阻礙緊急車輛通道的地方；c.燒烤場地與任何危險品貯存所／臨時構築物／大量的可燃物料須保持最少6米的安全距離；d.燒烤爐的數目及燒烤炭的數量應盡量減至最少；e.不可使用易燃液體或任何危險品作點火或燃燒用途；f.燒烤場地內應放置兩具9公升裝水劑或4.5公斤裝二氧化碳滅火器；g.進行燒烤活動時，應安排足夠員工在場看管；h.進行燒烤活動時，不可在燒烤場地同時舉行其他活動。火鍋活動：a.火鍋活動只可在上課以外的時間進行；b.只可使用電力，不得使用其他燃料或明火；c.進行火鍋活動時，應注意避免電力超出負荷，並須使用合適的爐具及火鍋盛器；d.於室內進行火鍋活動時，應保持空氣流通；e.進行火鍋活動的場地內總人數不可超過由教育局簽發的「容額證書」所訂明的最高限額；f.進行火鍋活動的場地內應放置兩具4.5公斤裝二氧化碳滅火器；g.進行火鍋活動時，應安排足夠員工在場看管。",
         keywords=["燒烤", "火鍋", "BBQ", "hotpot", "消防安全",
                   "6米", "9公升", "4.5公斤", "二氧化碳滅火器",
                   "容額證書", "電力", "上課以外", "學校行政手冊", "附錄5"],
         q="學校 燒烤 火鍋 消防"),

    dict(fid="sag_apx_principal_appt_docs",
         source_id="sag_2025_11", title="學校行政手冊", topic="general",
         url=f"{SAG_URL}#page=201",
         text="校長聘任申請要交咩文件？《學校行政手冊》Ch7 附錄1（註）："
              "申請校長聘任所需遞交的證明文件／資料（透過公開招聘／內部晉升甄選的校長）：1.有關招聘及甄選程序的文件／資料 — a.招聘過程的記錄（包括公開職位空缺的方法、接獲的申請書數目、初選及面試人數、獲選的申請人）；b.有份參與招聘工作的職員申報利益衝突的文件；c.公開招聘文件的副本；d.甄選準則（例如各範疇的比重及評分標準）；e.初選及面試的評核記錄；f.校長遴選委員會的組成；g.推薦擬任校長的理由；h.法團校董會／校董會通過聘用擬任校長的文件。2.擬任校長的個人資料文件副本：a.教師註冊證；b.工作簽證（如非本地居民）；c.學歷證明；d.校長資格認證（如未持有，需提交專業發展需要分析及／或擬任校長課程的證書／修讀證明）；e.由前任僱主發出列有校長過去實任職級的服務證明書；f.已填妥的「準僱員性罪行定罪紀錄查核」表格（如屬透過內部晉升的校長，毋須進行查核）；g.《基本法及香港國安法》測試及格成績證明（如屬透過內部晉升的校長，毋須參加測試）；h.已填妥的「查詢教員註冊資料申請表格」。所有文件副本須由學校校監簽署確認，須載有：(a)校監在「已查閱正本」字樣下簽署；(b)校監的姓名及職位；(c)查閱文件正本的日期。",
         keywords=["校長聘任", "principal appointment", "公開招聘",
                   "內部晉升", "甄選程序", "校長遴選委員會",
                   "教師註冊證", "校長資格認證", "性罪行查核",
                   "基本法測試", "校監簽署", "學校行政手冊", "附錄1"],
         q="校長 聘任 文件"),
]


def combine(text, kw):
    return text + " " + " ".join(kw)


def cos(a, b):
    s = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return s / (na * nb) if na and nb else 0.0


def load_service_key():
    k = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not k and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SUPABASE_SERVICE_KEY=") and not line.startswith("#"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return k


def headers_svc():
    svc = load_service_key()
    if not svc:
        sys.exit("ERROR: SUPABASE_SERVICE_KEY missing")
    return {"apikey": svc, "Authorization": f"Bearer {svc}", "Content-Type": "application/json"}


def fn_count(h):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&content_type=eq.footnote_curated",
        headers={**h, "Range-Unit": "items", "Range": "0-0", "Prefer": "count=exact"},
        timeout=40,
    )
    return r.headers.get("content-range", "?")


def id_lookup(h, cid):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&id=eq.{cid}", headers=h, timeout=40)
    return r.json()


def build_rows(vectors):
    rows = []
    for e, v in zip(F, vectors):
        rows.append({
            "id": f"footnote_fn_{e['fid']}", "hash": bw.text_hash(e["text"]), "text": e["text"],
            "source_id": e["source_id"], "title": e["title"], "url": e["url"],
            "topic": e["topic"], "content_type": "footnote_curated", "fact_type": "policy",
            "embedding": v,
        })
    return rows


def self_test():
    api = bw.load_api_key()
    ids = [f"footnote_fn_{e['fid']}" for e in F]
    print(f"entries={len(F)} unique_ids={len(set(ids))}")
    if len(set(ids)) != len(ids):
        # find duplicates
        seen = {}
        for i, cid in enumerate(ids):
            seen.setdefault(cid, []).append(i)
        dups = {k: v for k, v in seen.items() if len(v) > 1}
        print(f"DUPLICATE IDs: {dups}")
        sys.exit("FAIL: duplicate fids in F")
    fn_vecs = bw.embed_batch(api, [combine(e["text"], e["keywords"]) for e in F])
    q_vecs = bw.embed_batch(api, [e["q"] for e in F])
    print("=== per-entry cosine vs representative query (gate LEAD>=0.45) ===")
    weak = 0
    for e, fv, qv in zip(F, fn_vecs, q_vecs):
        c = cos(fv, qv)
        flag = "LEAD" if c >= 0.45 else ("merge" if c >= 0.42 else "WEAK")
        if c < 0.45:
            weak += 1
        print(f"  {c:.3f} [{flag:5}] {e['fid']}")
    print(f"=== {len(F)-weak}/{len(F)} >= 0.45 lead ===")


def execute():
    api = bw.load_api_key()
    h = headers_svc()
    print("=== INSPECT before ===")
    print("  footnote_curated count:", fn_count(h))
    for e in F:
        cid = f"footnote_fn_{e['fid']}"
        print(f"  id {cid} ->", id_lookup(h, cid))
    vectors = bw.embed_batch(api, [combine(e["text"], e["keywords"]) for e in F])
    rows = build_rows(vectors)
    hh = {**h, "Prefer": "resolution=merge-duplicates,return=minimal"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", headers=hh, json=rows, timeout=300)
    if resp.status_code not in (200, 201, 204):
        sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
    print("=== INSERT ok ===")
    print("=== INSPECT after ===")
    print("  footnote_curated count:", fn_count(h))
    missing = [f"footnote_fn_{e['fid']}" for e in F if not id_lookup(h, f"footnote_fn_{e['fid']}")]
    print("  missing after insert:", missing or "none")


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
