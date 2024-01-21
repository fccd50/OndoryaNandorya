import PySimpleGUI as sg

class Guidget:
    window_title = 'おんどりゃツール 2.6 K'
    window_size = (520, 420)
    def get_window(self, ports):
        self.ports = ports
        return sg.Window(title=self.window_title, size=self.window_size, layout=self.layout())

    def adjustment_tab(self):
        chuui = sg.Text("調整ボタン押したら30秒は待ってね")
        chuui2 = sg.Text("調整結果OKなら→を押してね")
        chuui3 = sg.Text("おんどりゃを再起動するなら←を押してね")
        tx_temp_pv = sg.Text("温度PV")
        tx_hum_pv = sg.Text("湿度PV")
        tx_pres_pv = sg.Text("気圧PV")
        tx_k_pv = sg.Text("水温PV")
        input_temp_pv = sg.Text(key='-temppv-',text="0.0")
        input_hum_pv = sg.Text(key='-humpv-',text="0.0")
        input_pres_pv = sg.Text(key='-prespv-',text="0.0")
        input_k_pv = sg.Text(key='-kpv-',text="0.0")
        input_temp_sv = sg.Input(size=(10,10),key='-temp-',enable_events=True,default_text="20.0")
        input_hum_sv = sg.InputText(size=(10,10),key='-hum-',enable_events=True,default_text="50.0")
        input_pres_sv = sg.InputText(size=(10,10),key='-pres-',enable_events=True,default_text="1000.0")
        input_k_sv = sg.InputText(size=(10,10),key='-k-',enable_events=True,default_text="20.0")
        col1 = [[tx_temp_pv],[input_temp_pv],[sg.Checkbox('温度SP', key='check_T')],[input_temp_sv]]
        col2 = [[tx_hum_pv],[input_hum_pv],[sg.Checkbox('湿度SP', key='check_H')],[input_hum_sv]]
        col3 = [[tx_pres_pv],[input_pres_pv],[sg.Checkbox('気圧SP', key='check_P')],[input_pres_sv]]
        col4 = [[tx_k_pv],[input_k_pv],[sg.Checkbox('水温SP', key='check_K')],[input_k_sv]]
        return [sg.Tab("調整",[[sg.Column(col1),sg.Column(col2),sg.Column(col3),sg.Column(col4)],
        [sg.Button('調整する', key='-adjust-',disabled=True), chuui],
        [chuui2,sg.Button(" 保存 ", key="-set-")],[sg.Button("RESET",key="-reset-"),chuui3 ]],key="-adjust_tab-")]

    def timeset_tab(self):
        timedisplay = sg.Text(key="-time-")
        return [sg.Tab("日時設定", [[timedisplay],[sg.Button("この時間でセット", key="-timeset-")]],key="-time_tab-")]
    def data_tab(self):
        return [sg.Tab("データ", [[sg.Button("データ取得",key="-getData-"),
                               sg.Text("    "),
                               sg.Button("データ保存",key="-savedata-"),
                               sg.Button("データ消去",key="-deldata-")],
                               [sg.Multiline(size=(100,14),key="-datafield-")]],key="-data_tab-")]
    def wifi_tab(self):
        return [sg.Tab("Wifi設定",[[sg.Text("SSID:")],[sg.InputText(size=(50,10), key="-ssid-")],[sg.Text("Password:")],[sg.InputText(size=(50,10), key="-paswd-")],[sg.Button("SET", key="-ssidOK-")],[sg.Text("", key="-ssidres-")]],key="-wifi_tab-")]
    def layout(self):
        title = sg.Text("おんどりゃなんどりゃツール 2.6 K", font=(242,18))
        return  [[title],
            [sg.Text("COMポート", font=(242,12))],
            [sg.Combo(self.ports, default_value="COM選択してね", size=(25,5),key='-ports-'),
            sg.Button('接続', key='-connect-'),sg.Text("",key="-status-")],
            [sg.TabGroup([self.adjustment_tab(),self.timeset_tab(),self.data_tab(),self.wifi_tab()],key="-tab-",enable_events=True)]
            ]
