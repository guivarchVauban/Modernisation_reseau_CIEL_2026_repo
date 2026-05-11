#!/usr/bin/env python3
"""
Générateur de fichiers XML de configuration pour Cisco 7942 (SIP)
Usage : python3 generate_cisco_xml.py ListeTelephones.xlsx

Règles :
  - Numéro de poste = numéro extrait du nom de salle (X113 -> 113)
  - Nom du fichier   = SEP{MAC_EN_MAJUSCULES}.cnf.xml
  - MAC en majuscules dans le nom de fichier uniquement
  - Mot de passe extension fixe : 123456789
  - Le script génère les fichiers XML dans un dossier "output/" à côté du script
"""

import sys
import os
import re
import openpyxl

# ─── CONFIGURATION GLOBALE (modifier ici si besoin) ───────────────────────────
FREEPBX_IP     = "192.168.10.1"
NTP_IP         = "145.238.80.83"
SSH_USER       = "cisco"
SSH_PASSWORD   = "cisco29200"
PHONE_PASSWORD = "29200"
AUTH_PASSWORD  = "123456789"
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATE = """<device>
    <deviceProtocol>SIP</deviceProtocol>
    <sshUserId>{ssh_user}</sshUserId>
    <sshPassword>{ssh_password}</sshPassword>
    <ipAddressMode>0</ipAddressMode>

    <devicePool>
        <dateTimeSetting>
            <dateTemplate>D/M/Ya</dateTemplate>
            <timeZone>GMT Standard/Daylight Time</timeZone>
            <olsonTimeZone>Europe/Paris</olsonTimeZone>
            <ntps>
                <ntp>
                    <name>{ntp_ip}</name>
                    <ntpMode>Unicast</ntpMode>
                </ntp>
            </ntps>
        </dateTimeSetting>

        <callManagerGroup>
            <members>
                <member priority="0">
                    <callManager>
                        <ports>
                            <ethernetPhonePort>2000</ethernetPhonePort>
                            <sipPort>5060</sipPort>
                        </ports>
                        <processNodeName>{freepbx_ip}</processNodeName>
                    </callManager>
                </member>
            </members>
        </callManagerGroup>
    </devicePool>

    <sipProfile>
        <sipProxies>
            <registerWithProxy>true</registerWithProxy>
        </sipProxies>
        <sipCallFeatures>
            <cnfJoinEnabled>true</cnfJoinEnabled>
            <rfc2543Hold>false</rfc2543Hold>
            <callHoldRingback>2</callHoldRingback>
            <localCfwdEnable>true</localCfwdEnable>
            <semiAttendedTransfer>true</semiAttendedTransfer>
            <anonymousCallBlock>2</anonymousCallBlock>
            <callerIdBlocking>2</callerIdBlocking>
            <dndControl>0</dndControl>
            <remoteCcEnable>true</remoteCcEnable>
            <callForwardURI>x-serviceuri-cfwdall</callForwardURI>
            <callPickupURI>x-cisco-serviceuri-pickup</callPickupURI>
            <callPickupListURI>x-cisco-serviceuri-opickup</callPickupListURI>
            <callPickupGroupURI>x-cisco-serviceuri-gpickup</callPickupGroupURI>
            <meetMeServiceURI>x-cisco-serviceuri-meetme</meetMeServiceURI>
            <abbreviatedDialURI>x-cisco-serviceuri-abbrdial</abbreviatedDialURI>
        </sipCallFeatures>

        <sipStack>
            <sipInviteRetx>6</sipInviteRetx>
            <sipRetx>10</sipRetx>
            <timerInviteExpires>180</timerInviteExpires>
            <timerRegisterExpires>3600</timerRegisterExpires>
            <timerRegisterDelta>5</timerRegisterDelta>
            <timerKeepAliveExpires>120</timerKeepAliveExpires>
            <timerSubscribeExpires>120</timerSubscribeExpires>
            <timerSubscribeDelta>5</timerSubscribeDelta>
            <timerT1>500</timerT1>
            <timerT2>4000</timerT2>
            <maxRedirects>70</maxRedirects>
            <remotePartyID>true</remotePartyID>
            <userInfo>None</userInfo>
        </sipStack>

        <autoAnswerTimer>1</autoAnswerTimer>
        <autoAnswerAltBehavior>false</autoAnswerAltBehavior>
        <autoAnswerOverride>true</autoAnswerOverride>
        <transferOnhookEnabled>false</transferOnhookEnabled>
        <enableVad>false</enableVad>
        <preferredCodec>g711alaw</preferredCodec>
        <dtmfAvtPayload>101</dtmfAvtPayload>
        <dtmfDbLevel>3</dtmfDbLevel>
        <dtmfOutofBand>avt</dtmfOutofBand>
        <alwaysUsePrimeLine>false</alwaysUsePrimeLine>
        <alwaysUsePrimeLineVoiceMail>false</alwaysUsePrimeLineVoiceMail>
        <kpml>3</kpml>
        <natEnabled>false</natEnabled>
        <phoneLabel>{extension}</phoneLabel>
        <stutterMsgWaiting>0</stutterMsgWaiting>
        <callStats>false</callStats>
        <silentPeriodBetweenCallWaitingBursts>10</silentPeriodBetweenCallWaitingBursts>
        <disableLocalSpeedDialConfig>false</disableLocalSpeedDialConfig>
        <startMediaPort>10000</startMediaPort>
        <stopMediaPort>20000</stopMediaPort>

        <sipLines>
            <line button="1">
                <featureID>9</featureID>
                <featureLabel>{feature_label}</featureLabel>
                <proxy>USECALLMANAGER</proxy>
                <port>5060</port>
                <name>{extension}</name>
                <displayName>{extension}</displayName>
                <autoAnswer>
                    <autoAnswerEnabled>2</autoAnswerEnabled>
                </autoAnswer>
                <callWaiting>3</callWaiting>
                <authName>{extension}</authName>
                <authPassword>{auth_password}</authPassword>
                <sharedLine>false</sharedLine>
                <messageWaitingLampPolicy>1</messageWaitingLampPolicy>
                <messagesNumber>*97</messagesNumber>
                <ringSettingIdle>4</ringSettingIdle>
                <ringSettingActive>5</ringSettingActive>
                <contact>{extension}</contact>
                <port>5060</port>
                <forwardCallInfoDisplay>
                    <callerName>true</callerName>
                    <callerNumber>true</callerNumber>
                    <redirectedNumber>false</redirectedNumber>
                    <dialedNumber>true</dialedNumber>
                </forwardCallInfoDisplay>
            </line>
        </sipLines>

        <voipControlPort>5060</voipControlPort>
        <dscpForAudio>184</dscpForAudio>
        <ringSettingBusyStationPolicy>0</ringSettingBusyStationPolicy>
        <dialTemplate>dialplan.xml</dialTemplate>
    </sipProfile>

    <commonProfile>
        <phonePassword>{phone_password}</phonePassword>
        <backgroundImageAccess>true</backgroundImageAccess>
        <callLogBlfEnabled>1</callLogBlfEnabled>
    </commonProfile>

    <loadInformation>SIP42.9-4-2SR3-1S</loadInformation>

    <vendorConfig>
        <disableSpeaker>false</disableSpeaker>
        <disableSpeakerAndHeadset>false</disableSpeakerAndHeadset>
        <pcPort>0</pcPort>
        <settingsAccess>1</settingsAccess>
        <garp>0</garp>
        <voiceVlanAccess>0</voiceVlanAccess>
        <videoCapability>0</videoCapability>
        <autoSelectLineEnable>0</autoSelectLineEnable>
        <webAccess>0</webAccess>
        <spanToPCPort>1</spanToPCPort>
        <loggingDisplay>1</loggingDisplay>
        <loadServer>{freepbx_ip}</loadServer>
        <sshAccess>0</sshAccess>
        <sshPort>22</sshPort>
    </vendorConfig>

    <versionStamp>002</versionStamp>
    <networkLocale>France</networkLocale>
    <networkLocaleInfo>
        <name>France</name>
        <uid>11</uid>
        <version>1.0.0.0-4</version>
    </networkLocaleInfo>

    <deviceSecurityMode>0</deviceSecurityMode>
    <authenticationURL></authenticationURL>
    <servicesURL></servicesURL>
    <directoryURL>http://{freepbx_ip}/directory.xml</directoryURL>
    <idleURL></idleURL>
    <informationURL></informationURL>
    <messagesURL></messagesURL>
    <proxyServerURL></proxyServerURL>
    <dialToneSetting>2</dialToneSetting>
    <dscpForSCCPPhoneConfig>96</dscpForSCCPPhoneConfig>
    <dscpForSCCPPhoneServices>0</dscpForSCCPPhoneServices>
    <dscpForCm2Dvce>96</dscpForCm2Dvce>
    <capfAuthMode>0</capfAuthMode>
    <capfList>
        <capf>
            <phonePort>3804</phonePort>
        </capf>
    </capfList>
    <transportLayerProtocol>2</transportLayerProtocol>
    <certHash></certHash>
    <encrConfig>false</encrConfig>
</device>
"""


def extraire_numero(nom_salle):
    """Extrait le numéro depuis le nom de salle. Ex: X113 -> 113"""
    match = re.search(r'\d+', str(nom_salle))
    if match:
        return match.group()
    return None


def generer_xml(mac, nom_salle, output_dir):
    extension = extraire_numero(nom_salle)
    if not extension:
        print(f"  [SKIP] Impossible d'extraire le numéro depuis '{nom_salle}'")
        return

    mac_upper = mac.strip().upper()
    feature_label = nom_salle.strip().upper()
    filename = f"SEP{mac_upper}.cnf.xml"
    filepath = os.path.join(output_dir, filename)

    content = TEMPLATE.format(
        ssh_user=SSH_USER,
        ssh_password=SSH_PASSWORD,
        ntp_ip=NTP_IP,
        freepbx_ip=FREEPBX_IP,
        extension=extension,
        feature_label=feature_label,
        auth_password=AUTH_PASSWORD,
        phone_password=PHONE_PASSWORD,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [OK] {filename}  ->  salle {nom_salle}, poste {extension}")


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 generate_cisco_xml.py <fichier.xlsx>")
        sys.exit(1)

    xlsx_file = sys.argv[1]

    if not os.path.isfile(xlsx_file):
        print(f"Erreur : fichier introuvable : {xlsx_file}")
        sys.exit(1)

    # Dossier de sortie = output/ à côté du script
    script_dir = os.path.dirname(os.path.abspath(xlsx_file))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nLecture de : {xlsx_file}")
    print(f"Dossier de sortie : {output_dir}\n")

    wb = openpyxl.load_workbook(xlsx_file, read_only=True)
    ws = wb.active

    # Détecter les colonnes depuis l'en-tête
    headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]

    try:
        col_salle = headers.index(next(h for h in headers if "salle" in h or "num" in h))
        col_mac   = headers.index(next(h for h in headers if "mac" in h))
    except StopIteration:
        print("Erreur : colonnes 'salle' ou 'mac' introuvables dans le fichier Excel.")
        print(f"Colonnes détectées : {headers}")
        sys.exit(1)

    count = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        nom_salle = row[col_salle]
        mac       = row[col_mac]

        if not nom_salle or not mac:
            continue

        generer_xml(str(mac), str(nom_salle), output_dir)
        count += 1

    print(f"\n{count} fichier(s) XML généré(s) dans : {output_dir}")


if __name__ == "__main__":
    main()
