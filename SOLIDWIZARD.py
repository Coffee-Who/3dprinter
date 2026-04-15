import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Menu } from "lucide-react";

export default function Portal() {
  const [dark, setDark] = useState(true);
  const [mobile, setMobile] = useState(false);
  const [openProduct, setOpenProduct] = useState(false);

  const theme = dark
    ? "bg-gray-950 text-white"
    : "bg-white text-gray-900";

  const cardStyle = dark
    ? "bg-gray-900 hover:bg-gray-800"
    : "bg-gray-100 hover:bg-gray-200";

  const LinkCard = ({ title, url }) => (
    <a href={url} target="_blank" rel="noreferrer">
      <Card className={`cursor-pointer transition-all rounded-2xl shadow-md p-2 ${cardStyle}`}>
        <CardContent className="text-center py-6 font-semibold text-lg">
          {title}
        </CardContent>
      </Card>
    </a>
  );

  const Grid = ({ children }) => (
    <div className={mobile ? "grid grid-cols-1 gap-3" : "grid grid-cols-3 gap-4"}>
      {children}
    </div>
  );

  return (
    <div className={`min-h-screen transition-all p-6 ${theme}`}>
      {/* Top Bar */}
      <div className="flex justify-between items-center mb-6">
        <div className="text-2xl font-bold">🏢 實威國際入口網站</div>

        <div className="flex gap-2">
          <Button onClick={() => setMobile(!mobile)}>
            <Menu className="w-4 h-4 mr-1" /> {mobile ? "電腦版" : "手機版"}
          </Button>

          <Button onClick={() => setDark(!dark)}>
            {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Internal Systems */}
      <h2 className="text-xl font-bold mb-3">🔧 內部系統</h2>
      <Grid>
        <LinkCard title="CRM 客戶管理" url="http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx" />
        <LinkCard title="EIP 企業入口" url="http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx" />
        <LinkCard title="EASYFLOW 簽核" url="http://192.168.100.85/efnet/" />
        <LinkCard title="請假系統" url="http://192.168.2.251/MotorWeb/CHIPage/Login.asp" />
      </Grid>

      {/* Official */}
      <h2 className="text-xl font-bold mt-8 mb-3">🌐 官方資源</h2>
      <Grid>
        <LinkCard title="實威官網" url="https://www.swtc.com/zh-tw/" />
        <LinkCard title="YouTube 官方" url="https://www.youtube.com/@solidwizard" />
        <LinkCard title="智慧製造 YouTube" url="https://www.youtube.com/@SWTCIM" />
        <LinkCard title="實威知識+" url="https://www.youtube.com/@實威知識" />
      </Grid>

      {/* Products */}
      <div className="mt-10">
        <button
          onClick={() => setOpenProduct(!openProduct)}
          className="text-xl font-bold mb-3"
        >
          🧩 產品入口 {openProduct ? "▲" : "▼"}
        </button>

        {openProduct && (
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">SOLIDWORKS</h3>
              <Grid>
                <LinkCard title="官方網站" url="https://www.solidworks.com/" />
              </Grid>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Formlabs</h3>
              <Grid>
                <LinkCard title="Formlabs 官網" url="https://formlabs.com/" />
                <LinkCard title="Support" url="https://support.formlabs.com/s/?language=zh_CN" />
              </Grid>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="text-center text-sm opacity-50 mt-10">
        SWTC Internal Portal © 2026
      </div>
    </div>
  );
}
