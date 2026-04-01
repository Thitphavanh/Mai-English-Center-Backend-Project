import os
import django
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from academics.models import Student, Course, ClassSchedule, Enrollment
from django.contrib.auth.models import User
from django.utils import timezone
import random

raw_data = """
ລາຍຊື່ນັກຮຽນ 05:30-06:30			Class C  Frimer ເຫຼັ້ມ3  ອາຈານດາວໃຈ			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  500,000 		
No.	ID STUDENT	First name	Nick Name	phone number 	TUITION FEE	Remark
1	00361	 MS PAIVNA	 KHAIMUK	020 58964899		
2	00354	MS LANIDA KONGTHILAT	BANA	020 55395777		
3	00458	MR XAYPHASUK	HOT	020 95931995		
4	00528	MR THANAXAY INTHAVONGSA	MESSI	020 96355422		
5	00591	MR NAVIN NAWEXAY	HONEY	020 55959592		
6	00773	ທ້າວ ສະຫຼາດ ສົມລາດ	ບິກບອຍ	020 52091298		
7	00777	ທ້າວ ເພັດຕະວັນ ສີວິໄລສຸກ	ຊັນ	020 94244458		
8	00652	ນາງ ທິບທິດາ	ເໝີຍລີ້	020 55475453		
9	00006-MEC	MR NANTHAKONE	DEW	020 99889761		
10	00769	ນາງ ທິດດາວພອນ ຫຸມມະນີວົງ	ນາງ	020 99794662		
11	00638	ນາງ ມີນາໄຊ ວົງທິສານ	ເມລີ້	020 79919599		
12	00630	ນາງ ສຸດາທິບ ໄພສິດ	ຕິ໋ງນ໋ອຍ	020 98945222		
13	00461	MS PHITSAMAY XAYKHUNNAVISET	YAYA	 020 96476213		
14	00513	MS Souphatta Litthanouvong	TANOY	020 56602388		
15	00456	MS PATHOUTHONG SANGSATHIEN	TOUKTA	020 55442342		
16	00164-MEC	MS JHINDASAVANH	A LIN	 020 98775744 		
17	00235-MEC	MR MAWIN	NEW	 020 98775744		
18	00509	MS NALISAVANH PHASAVAT	KHAIMOUK	020 99618188		
19	00723	ນາງ ໂຊຕິກາ ພຸກແສງນາ	ສົ້ມໂອ	020 23434361		
20	00739	ນາງ ອໍລະດີ ຂັນສຸລິວົງ	ເໝີຍ	020 99840892		
21	00618	MR Thavikhoun Chanthavongsa	Donat	020 56612540		
22	00724	ນາງ ທິດາວັນ ເຜົ່າພົງສະຫວັດ	ມິມີ່	020 78223707		
23	00804	ທ້າວ ວັນຊະນະ ດາລາວົງ	ໄອເດຍ	020 55199456		

ລາຍຊື່ນັກຮຽນ 06:30-07:30			Class C  Frimer ເຫຼັ້ມ3  ອາຈານດາວໃຈ			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	phone number 	TUITION FEE	Remark
1	00371	MS SOULIPHONE	LIENMAY	020 28932295		
2	00373	MS PHOUMIPHONE VATANA	IG	020 99840886		
3	00390	MR TONKA	TONKA	020 55642330		
4	00344-MEC	MR SINNALAT PHIMMASAN	CU TUAN	 020 76002299		
5	00594	ນາງ ອະລິສາ ສຸວັນນະແສງ	ບິວ	020 99299352		
6	00598	ທ້າວ ຊອນມາ ຜິວທຳມະວົງ	ຊອນ	020 96611662		
7	00374	MS PHETPHAILIN SIVILAY\	NEIY 	020 96989886		
8	00741	ນາງ ອິນນາລິນ ສຸລິວົງ	ອິນນາ	020 91684995		
9	00497	ນາງ ອຸດາວັນ ຊຸມພົນພັກດີ	ຄິດຕຣີນ	 020 55665544		
10	00540	MR PHILAPHON	 IDIW	020 56729988		
11	00541	MS PHILAYA	VIEWNA	020 56729988		
12	00635	ທ້າວ ນັດທະສິດ ບຸນນະລາດ	ນາຍ	020 94181599		SCHOLARSHIP
13	00637	ທ້າວ ຄຳທະວີສຸກ ສີປະເສິດ	ແບ້ງ	020 22608603		
14	00639	ທ້າວ ທະນາກອນ ພະພິລົມ	ຄິວ	020 52477868		
15	00619	MR Sittisak Sipasert	Bobby	020 22608603		
16	00246-MEC	MS MOUKSAVANH KHONGMANEE	ມຸກ	020 97728222		
17	00800	ນາງ ທິດາປັນຍາວົງ ເຫມມະນີ	ນ້ຳຟ້າ	020 55063687		
18	00631	ນາງ ສິລິມົນ ເທບຄຳຜົງ	ນຸດນີ້	020 95959650		
19	00820	ທ້າວ ສະນະກັນ ບຸນເພັດຕາວັນ	ບ໋ອນ	020 22669922		
20	00821	ນາງ ຈິນລະກັນດາ ປັນຍາທິບ	ແອັມດາ	020 22669922		
21	00375	MR PHENGPASERT VILAYSUK	TITAN	020 91119946		
22	00524	MR KITISAK DALAHEAUNG	NINE	 020 77383838		
23	00830	ນາງ ອັນມິນຕາ ບູນເພັດຕາວັນ	ມິນ	020 22669922		
24	00832	ນາງ ກາໜົກກອນ ບຸດຕະວົງ	ນ້ຳໃສ	020 54659424		

ລາຍຊື່ນັກຮຽນ 05:30-06:30			Class D  Frimer ເຫຼັ້ມ2  ອາຈານຈັນທະລາ			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	phone number 	TUITION FEE	Remark
1	00603	MR Keopanya Patthana	Ball	020 96936743		
2	00606	MR Xayyawat Suliya	Tono 	020 58606299		
3	00608	MS Soudaphone Singphuangphet	Nong 	020 22408584		
4	00610	MS Souphavady Latchachak	King	020 58697966		
5	00682	MS Thipkesone Boudsomsi	Kitty	020 22746197		
6	00614	MR Xayyalat Nuanmanee	Mouyong	020 28083088		
7	00615	MS Pavina Heungsuliya	LookPa	020 55319296		
8	00616	MS Phetmanee Thammavong	Ploysai	020 97261424		
9	00617	MR Phoumeexay Thammavong	Phou	020 97261424		
10	00491	MS DAVIKA PHETXOMPHOU	BELLA	020 98566613		
11	00527	MS THANISONE INTHAVONGSA	ELLY	020 96355422		
12	00685	MS Latda Khampian	Nounim	020 52899828		
13	00686	MS Manida Xaybuasi	Meiy	020 91795128		
14	00688	MR Souliyon Bolibun	Nampou	020 92735426		
15	00623	MS Marnpha Phomphakdy	Angie	020 98669895		
16	00709	MS Anda Cole	 Anda	020 56127647		
17	00467	MR Thavatxay Chanthavong	ກຸຕຸ່ງ	020 99558565		
18	545	MS FASAI LUSOMBOUN	THING THING	020 96324141		
19	00818	MS Pavina Inthatilath	Bella	020 99235599		
20	00799	ທ້າວ ຫັດສະຫວັນ ພັນທຸລາດ	ອາຕີ້	020 91526840		
21	00282-MEC	ທ້າວ ທະວີຊັບສະຫວັນ	WINNER	 020 77743123		
22	474	ທ້າວ ໂຊກອານັນ	ໂກແບັກ	020 52277666		
23	00014-MEC	MS FASAI CHANTHADUANGSY	FA	020 93361225		
24	00155-MEC	MS VANTIDA KHETTAVONG	CHAMMY	 020 59404324 		
25	00280-MEC	MR PHOUMEPHON	Neuang	020 59038591		

ລາຍຊື່ນັກຮຽນ 06:30-07:30			CLASS D  NEWWORLD 3 ອາຈານ ຈັນທະລາ			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1	00037-MEC	MR ANON SIVILAY	QUOC			SCHOLARSHIP
2	00481-MEC	MS NAVALAT PHISITNAN	NALINH	020 51516356		SCHOLARSHIP
3	00482-MEC	MS ALISA KONEMANIVONG	MINY	020 55646945		SCHOLARSHIP
4	00034-MEC	MR VILAPHAP SIVILAY	MEE 			SCHOLARSHIP
5	00046-MEC	MR Anisone	Tono	020 22669977		
6	00728	MR XAYYASONE DUANGPASERT	GAME	020 77744447		

ລາຍຊື່ນັກຮຽນ 10:00-12:00			Class A  Frimer ເຫຼັ້ມ1  ອາຈານແນັດ			ເສົາ-ອາທິດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1	00642	ນາງ ອານິຊາ ສຸວັນດີ	ໂກເບລ	020 92222377		
2	00643	ນາງ ມາລິສາ ສຸວັນດີ	ແອນນາ	020 92222377		
3	00644	ນາງ ອາລິຊາ ຍົດໄຊວິບຸນ	ອາລິດ	020 95092888		
4	00645	ທ້າວ ໄຊປັນຍາ ຍົດໄຊວິບຸນ	ອາເທີ້	020 95092888		
5	00704	ທ້າວ ສະຫວັນຄຳ ແສນຄຳພູ	ຢູໂລ	020 97358326		
6	00705	ນາງ ວິມາລາ ທອງອິນ	ນ້ຳຝົນ	020 77480870		
7	00661	ນາງ ຫົງຟ້າ ໂຄ	ຫົງຟ້າ	020 55441444		
8	00662	ທ້າວ ມະນີເນດ ຫຼ້າມະນີວົງ	ມິໂນ່	020 55441444		
9	00663	ທ້າວ ຖະໜອມຊັບ ເນົາວະລັງສີ	ບີເອັມ	020 22324445		
10	00664	ນາງ ມຸກທິດາ	ໄຂ່ມຸກ	 020 96564349 		
11	00669	ທ້າວ ຄູນຊັບ ເທບພະສອນ	ອໍໂຕ້	020 98885525		
12	00670	ນາງ ພຸດທິຕາ ເທບພະສອນ	ອໍລ້າ	020 98885525		
13	00671	ນາງ ນິດທິດາ ແສງບຸດຕາ	ນີນ້າ	020 93211132		
14	00677	ທ້າວ ຈັນທະສອນ ສັກໄພວັນ	ບ໋ອນ	 020 78325559		
15	00679	ນາງ ອຸດົມຊັບ ໂຄດສົມບັດ	ຊົມພຸ້	020 98058580		
16	00680	ນາງ ແກ້ວມະນີ ວັນນະພຸມ	ແອນນີ້	020 52946954		
17	00746	ນາງ ໃບບຸນ ໄຊຍະແສງ	ໝູທອງ	020 98557666		
18	00809	ນາງ ປິຍະທິດາ ນິລະໄຊ	ແອັມມ່າ	020 97507171		
19	00810	ທ້າວ ທານຸສິດ ນິລະໄຊ	ຄີລຽນ	020 97507171		
20	00812	ນາງ ອຸດົມຊັບ ພຸດທະເສນ	ແຮັບປີ້	020 28384551		
21	00813	ທ້າວ ທະວີໂຊກ ພຸດທະເສນ	ຣັກກີ້	020 28384551		
22	00568	ທ້າວ ທັນວາ ບົວໄລຫົງ	ເກັ່ງ	020 96937241		

ລາຍຊື່ນັກຮຽນ 10:00-12:00			Class B  Frimer ເຫຼັ້ມ1  ອາຈານອໍ້			ເສົາ-ອາທິດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1	00707	ທ້າວ ທະນະພັດ ບຸນພາຄົມ	ມ້ອນ	 020 54065555		
2	00150-MEC	MS THIPSAVANH	NO AN	 020 54065555		
3	00729	ທ້າວ ອຳນາດ ລູສົມບູນ	ຫາວ	020 96324141		
4	00732	ທ້າວ ສຸກັນ ທອງວິໄລສັກ	ອາເກມ	020 95133400		
5	00736	ທ້າວ ທະນະທອນ ພັນມີໄຊ	ເອັກຕ້າ	020 54066693		
6	00737	ທ້າວ ທະນະເດດ ພັນມີໄຊ	ຈູເນ່ຍ	020 54066693		
7	00745	MS CHANHDALY KEOVONGNGEUN	WENDY	 020 59034299		
8	00746	ທ້າວ ສັນຕິພາບ ໄຊຈະເລີນ	ກັບຕັນ	020 59395654		
9	00748	ທ້າວ ພິສີດ ແກ້ວມີໄຊ	ອໍໂຕ້	 020 95295222		
10	00780	ທ້າວ ພູລິເດດ ທຳມະຈັນ	ອັສຕິນ	 020 55114289		
11	00781	ທ້າວ ນາລົງສັກ	ຄຣີດ	 020 55114289		
12	00785	ທ້າວ ສູກທະວີຊັບ ເກດຕະວົງ	ມິນຕັ້ນ	 020 77772539		
13	00792	ທ້າວ ເທບທັນວາ ຊາມຸນຕີ	ນະເດດ	 020 95670529		
14	00400	MS NALITA DAOVIJIT	NAMNIN	020 55282620		
15	00811	ທ້າວ ທະດາໄຊ ສຸກຄຳທັດ	ເຂົ້າພູນ	 020 29804886 		
16	00658	ທ້າວ ເພັດສະຫວັນ ນາຕາເຈົ້າ	ອໍກ້າ	 020 98215456 		
17	00814	ທ້າວ ພອນພາສຸກ ບຸນນາລາ	ແຈມມິນ	020 98393947		
18	00820	ທ້າວ ດີໂດ້ ຈິນດາ	ດີໂດ້	020 96981297		
19	00821	ນາງ ພອນສະຫວັນ ສູ່ເສນ	ນິນນີ້	020 99752531		
20	00823	ທ້າວ ຈະເລີນຊັບ ແກ້ວມະນີໄຊ	ເຕຊິນ	 020 96725420		
21	716	ທ້າວ ເພັດປະເສີດ ໄຊຍະລິນທອງ	ອາລັນ	020 56395161		

ລາຍຊື່ນັກຮຽນ 10:00-12:00			Class C  Frimer ເຫຼັ້ມ1  ອາຈານອຸ່ນເພັດ			ເສົາ-ອາທິດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1	00108-MEC	MS SOMPHONEPHET SAVANH	EM LAN	 020 52929898		
2	00659	ທ້າວ ມັງກອນ ໂຄ	ມັງກອນ	020 55441444		
3	00483	MR OUDOMXAP XOUMPHONPHAKDY	ARUN	020 99975424		
4	00544	MR PHOKHAM	SAM	020 98645075		
5	00266-MEC	MS VIPHALY PHAXAYSOMBAT	NAMKHING	020 23262934		
6	00520	ນາງ ນ້ຳຟ້າ ມະນີບົດ	ນ້ຳຟ້າ	020 97955558		
7	559	MR XAYYAPHONE	DEW	 020 96564349 		
8	00651	ທ້າວ ພຸດທະກອນ ສັກໄພວັນ	ບອຍ	020 55446631		
9	00699	ນາງ ພອນສະຫວັນ ຈະເລີນສຸກ	ເດຍ	020 78089709		
10	508	ນາງ ວາດສະຫນາ	ໄຂ່ມຸກ	020 54510991		
11	599	ທ້າວ ຫັດທະພອນ ສີລາວີ	ບິວ	020 55440808		
12	00802	ທ້າວ ສິດທິເດດ ປ້ອງວິໄລ	ອຸບົນ	020 23295653		
13	558	MR SOUNED	 LIANKHAM	  020 55979494  		
14	00824	ນາງ ດະມິດສະລາ ຈັນທະລັງສີ	ອັນຊັນ	020 55387799		
15	00735	ທ້າວ ສຸກສາຍຄຳ ໄຊຍະລິນທອງ	ຕົ້ນກ້າ	 020 52466359		
16	00805	ທ້າວ ສິລິຊັບ ຈັນມະພົນ	ຊັບປີ້	 020 55888495		
17	717	ນາງ ດາວສະຫວັນ ສະຫວັນຈັນດີ	ກິມຫງັອກ	  020 55959024 		

ລາຍຊື່ນັກຮຽນ 10:00-12:00			Class D  Frimer ເຫຼັ້ມ2  ອາຈານຈັນທະລາ			ເສົາ-ອາທິດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1	00091-MEC	MR LITHIDET MOONTHILAT	JONO	 020 22213255		
2	00484	MR ATIT XOUMPHONPHAKDY	SUNDAY	020 99975424		
3	00461	MR XAYXANA	NAT	020 55226662		
4	00567	MS SOUKPHAPHONE 	KIMMY	020 98552552		 SCHOLARSHIP
5	00411	MS INTHADA	KHAOMAI	 020 29804886 		
6	00579	MR THANAPHON	KA	020 97462814		
7	00198-MEC	MR ANOUSONE SYSOUVAN	BEEM	 020 55641319		
8	00199-MEC	MR PHOUDTASONE SYSOUVAN	BORM	 020 55641319		
9	00414	ທ້າວ ຕ່າຍດັງຄວາ	BOY			
10	00667	ນາງ ພອນທິດາ ຊົງສີ	ເພັນນີ້	020 91179199		
11	00700	ທ້າວ ທະນະກິດ ສະຫວັນຈັນດີ	ປາວານ	020 91852122		
12	00797	ທ້າວ ທັນວາ ໄຊຍະພອນ	ເຊບ	020 99464317		
13	00825	ທ້າວ ຊັບນາຄອນ ທຳມະວົງສາ	ອັງເປົາ	020 29893222		
14	00826	ນາງ ປະຫວັດໄຊ ທຳມະວົງສາ	ປັນ ປັນ	020 29893222		
15	00295-MEC	ທ້າວ ເລຮິ້ວຢາບ້າວ	BAO	 020 95179689		
16	00296-MEC	ນາງ ເລງ໋ອກບາວອານ	NOM	020 95179689		
17	00360	ທ້າວ ໄຊຊະນະ ວໍລະບຸດ	 ເຈັ໋ງໆ	020 98126157		
18	00803	ນາງ ວັນວິສາ ແກ້ວຄຳໂພ	ອາລິດ	 020 56545851		
19	00805	ທ້າວ ສິລິຊັບ ຈັນມະພົນ	ຊັບປີ້	 020 55888495		

ລາຍຊື່ນັກຮຽນ 10:00-12:00			Class E  Frimer ເຫຼັ້ມ3  ອາຈານດາວໃຈ			ເສົາ-ອາທິດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1	00094-MEC	MS ALADA KEOMIXAY	MINY	 020 95295222		
2	00028-MEC	MS THIPPANYA XAYKUNLANG	YUME	 020 55955504		
3	00107-MEC	MS SOMSANUK SAVANH	EM HEUANG	 020 52929898		
4	00302-MEC	MS PHOYPHAILIN	KHAIMUK 	 020 54283678		
5	00256-MEC	MR PHONEPHANSA	KOUGNANG	020 52172888		
6	00070-MEC	MR MANGKONESOK SIDALA	BEAR	020 98949222		
7	00267-MEC	MR LATANAVIXAY PHAXAYSOMBAT	KHUN	 020 56192456 		
8	00356	MR KHUNKHAM	TAK	020 55246951		
9	00405-MEC	MR SANYAHAK	Xaiy	020 52172888		
10	00454	MR LERNGXAY CHANTAVONG	TOIY	020 91947419		
11	00440	MR LIENXAY	LIENXAY	020 55979494		
12	00653	ນາງ ຮວງເຍືອງລິນຊານ	ລີນຊານ	020 91113789		
13	00654	ນາງ ຮວງເຍືອງຢາເຮີນ	ແກຣມ	020 91113789		
14	00576	MR Santhakone	San	 020 52485430		
15	00098-MEC	MR TITON	TITON	 020 22669977		
16	00415	ທ້າວ ຕ່າຍເຊິນ	BAND	 020 91735160		
17	00734	ທ້າວ ພີລາໂນ້	ໂນ້	020 55226662		
18	00747	MS NEELAVANH KEOVONGGNGEUN	MAKEE	 020 59034299		
19	00097-MEC	MS MITSAKHA PHONESAVANH	TINA	 020 98989696		
20	00071-MEC	MR VANNASIN VOLABOUD	HENG HENG	 020 58692119 		SCHOLARSHIP
21	00008-MEC	MS MEKHALA	POPPY	020 55199456		SCHOLARSHIP

ລາຍຊື່ນັກຮຽນ 06:30-07:30			Class E ພາສາຈີນ 1 ອາຈານ ເສີນ			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1	00751	ທ້າວ ໄຊສົມພອນ ລິນຊົມພູ	ຕຸລາ	 020 22300121		
2	00752	ນາງ ສຸກພາພອນ ຄົມທິລາດ	ຄິມມີ້	020 98552552		
3	00753	ນາງ ສຸພາພອນ ເດດອຸດົມສັກ	ໂບວີ້	 020 55633132		
4	00756	ນາງ ມ່ານຟ້າ ພົມພັກດີ	ແອັ໋ນຈີ້	020 98669895		
5	00760	ທ້າວ ໄຊຍະວັດ ສຸລິຍາ	ໂຕໂນ້	020 58606299		
6	00771	ນາງ ມະນີຈັນ ພົມມະຈັກ	ຈີຢອນ	020 78067888		
7	00772	ທ້າວ ຈັນທະສອນ ສີປະເສີດ	ບອນ	020 99914035		
8	00774	ນາງ ເທບສຸດາພອນ ສິນນະວັງທອງ	ລີ້	 020 77719517		
9	00775	ນາງ ວັນນະພາ ເຜົ່າພົງສະຫວັດ	ໃບເພີນ	 020 78223707		
10	00801	ນາງ ສຸດທິດາ ດວງທຳມະວົງ	ແອັມເຮືອງ	020 58393939		
11	00723	ນາງ ໂຊຕິກາ ພຸກແສງນາ	ສົ້ມໂອ	020 23434361		
12	00795	ທ້າວ ສັນຕິສຸກ ຂຽວລືເດດ	ບອສ	ລູກອາຈານດາວ	 SCHOLARSHIP	
13	00806	ທ້າວ ພອນປະເສີດ ຄຳມະນີວົງ	ແບັ້ງ	020 93047723		
14	00013-MEC	ນາງ ຊິນນະພອນ	ບີບີ່	 020 55244166		

ລາຍຊື່ນັກຮຽນ 06:30-07:30			CLASS VIP TEACHER JOE (EX REATE 700)			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  1,750,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1		KEVALIN SIVILAY	NINA	 020 9511 5252	  1,750,000.00 	2.500 ບາດ
2		VANIDA SIVILAY	NADA	 020 9511 5252	  1,750,000.00 	2.500 ບາດ
3		ORJUNE	TONHOM		  1,750,000.00 	2.500 ບາດ
4		TONHOM	ORJUNE		  1,750,000.00 	2.500 ບາດ

ລາຍຊື່ນັກຮຽນ 06:30-07:30			CLASS VIP TEACHER JOE (EX REATE 700)			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  3,500,000 	Mar-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1		BOW	BOW		  3,500,000.00 	5.000 ບາດ
2		GOLF	GOLF		  3,500,000.00 	5.000 ບາດ

ລາຍຊື່ນັກຮຽນ 07:30-08:30			CLASS VIP TEACHER JOE (EX REATE 700)			ຈັນ-ພະຫັດ
			 TUITION FEE	 LAK  3,500,000 	Feb-26	
No.	ID STUDENT	First name	Nick Name	Phone number 	TUITION FEE	Remark
1		MR SOUTHIPHON INTHITHEP	NAWIN	 020 22300121	  3,500,000.00 	5.000 ບາດ
2		MS NATTHA INTHITHEP	LINNA	020 98552552	  3,500,000.00 	5.000 ບາດ
"""

def extract_instructor(header_line):
    # Find words after 'ອາຈານ'
    match = re.search(r'ອາຈານ\s*([^\s\t]+)', header_line)
    if match:
        name_frag = match.group(1).strip()
        # Find user
        users = User.objects.filter(first_name__icontains=name_frag)
        if users.exists():
            return users.first()
    if 'TEACHER JOE' in header_line:
        joe, _ = User.objects.get_or_create(first_name='Joe', defaults={'username':'teacher_joe', 'is_staff':True})
        return joe
    
    # Try finding "ອາຈານແນັດ", "ອາຈານອໍ້", "ອາຈານຈັນທະລາ"
    if 'ແນັດ' in header_line:
        t, _ = User.objects.get_or_create(first_name='ແນັດ', defaults={'username':'teacher_nat', 'is_staff':True})
        return t
    if 'ອໍ້' in header_line:
        t, _ = User.objects.get_or_create(first_name='ອໍ້', defaults={'username':'teacher_or', 'is_staff':True})
        return t
    if 'ຈັນທະລາ' in header_line:
        t, _ = User.objects.get_or_create(first_name='ຈັນທະລາ', defaults={'username':'teacher_chantala', 'is_staff':True})
        return t
        
    return None

import random
def generate_student_id():
    while True:
        sid = f"NEW-{random.randint(1000, 99999):05d}"
        if not Student.objects.filter(student_id=sid).exists():
            return sid

print("Parsing detailed data...")
blocks = [b.strip() for b in raw_data.split('\n\n') if 'ລາຍຊື່ນັກຮຽນ' in b]

count = 0
for block in blocks:
    lines = block.split('\n')
    header_line = lines[0]
    
    # Extract time slot
    time_match = re.search(r'(\d{2}:\d{2}-\d{2}:\d{2})', header_line)
    time_slot = time_match.group(1) if time_match else "Unknown"
    
    # Extract ClassName (e.g. Class C, CLASS D, Class E ພາສາຈີນ 1)
    class_match = re.search(r'(Class[^\t]+|CLASS[^\t]+)', header_line, re.IGNORECASE)
    class_name = class_match.group(1).strip() if class_match else "VIP Class"
    # cleanup class_name
    class_name = re.sub(r'ອາຈານ.*$', '', class_name).strip()
    
    teacher = extract_instructor(header_line)
    
    course, _ = Course.objects.get_or_create(name=class_name)
    cs, _ = ClassSchedule.objects.get_or_create(
        course=course, time_slot=time_slot,
        defaults={'start_date': timezone.now().date(), 'end_date': timezone.now().date()}
    )
    if teacher:
        cs.teacher = teacher
        cs.save()
        
    # Read rows
    for line in lines:
        if line.startswith('No.') or line.startswith('ລາຍຊື່ນັກຮຽນ') or line.startswith('ຍອດລວມ') or line.startswith('TUITION'):
            continue
            
        parts = line.split('\t')
        if len(parts) >= 4 and parts[0].strip().isdigit():
            stu_id = parts[1].strip()
            fname = parts[2].strip()
            nname = parts[3].strip()
            phone = parts[4].strip() if len(parts) > 4 else ""
            
            if not fname and not nname:
                continue
                
            if not stu_id:
                stu_id = generate_student_id()
                
            student, created = Student.objects.update_or_create(
                student_id=stu_id,
                defaults={
                    'full_name': fname if fname else nname,
                    'nick_name': nname,
                    'phone_number': phone
                }
            )
            Enrollment.objects.get_or_create(
                student=student,
                class_schedule=cs,
                defaults={'enrollment_date': timezone.now().date()}
            )
            count += 1

print(f"Successfully processed {count} student records with full details!")
