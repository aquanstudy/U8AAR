#encoding:utf-8
#Author:xiaohei
#CreateTime:2014-10-25
#
# The config operations. some defined in xml some defined in sqldb.
#
#
import sys
import os
import os.path
import file_utils
import log_utils
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree


def getLocalConfig():
    configFile = file_utils.getFullPath("config/local/local.properties")
    if not os.path.exists(configFile):
        log_utils.error("local.properties is not exists. %s " % configFile)
        return None

    cf = open(configFile, "r")
    lines = cf.readlines()
    cf.close()

    config = {}

    for line in lines:
        line = line.strip()
        dup = line.split('=')
        config[dup[0]] = dup[1]

    return config


def getToolVersion():
    config = getLocalConfig()
    if config and "tool_versionName" in config:
        return config['tool_versionName']

    return "unkown"


def getJDKHeapSize():
    config = getLocalConfig()
    if config and "jdk_heap_size" in config:
        return config['jdk_heap_size']

    return 512

def get_py_version():
    version = sys.version_info
    major = version.major
    minor = version.minor
    micro = version.micro

    currVersion = str(major)+"."+str(minor)+"."+str(micro)

    return currVersion

def is_py_env_2():

    version = sys.version_info
    major = version.major
    return major == 2

def getAllGames():
    """
        get all games
    """
    configFile = file_utils.getFullPath("games/games.xml")
    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except Exception as e:
        log_utils.error("can not parse games.xml.path:%s", configFile)
        return None

    gamesNode = root.find('games')
    if gamesNode == None:
        return None

    games = gamesNode.findall('game')

    if games == None or len(games) <= 0:
        return None

    lstGames = []
    for cNode in games:
        game = {}
        params = cNode.findall('param')
        if params != None and len(params) > 0:
            for cParam in params:
                key = cParam.get("name")
                val = cParam.get("value")
                game[key] = val

        logNode = cNode.find('log')
        if logNode != None:
            game['log'] = dict()
            logParams = logNode.findall('param')
            if logParams != None and len(logParams) > 0:
                for lParam in logParams:
                    key = lParam.get("name")
                    val = lParam.get('value')
                    game['log'][key] = val

        lstGames.append(game)

    return lstGames


def getTestKeyStore():
    keystore = {}
    keystore['keystore'] = "config/keystore/xiaohei.keystore"
    keystore['password'] = "xiaohei"
    keystore['aliaskey'] = "xiaohei"
    keystore['aliaspwd'] = "xiaohei"

    return keystore


def getKeystore(appName, channelId):
    lstKeystores = getAllKeystores(appName)
    if lstKeystores != None and len(lstKeystores) > 0:
        for keystore in lstKeystores:
            if keystore['channelId'] == channelId:
                return keystore

    return getDefaultKeystore(appName)


def getDefaultKeystore(appName):
    fileName = "games/" + appName + "/keystore.xml"
    configFile = file_utils.getFullPath(fileName)
    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except Exception as e:
        log_utils.error("can not parse keystore.xml.path:%s", configFile)
        return None

    params = root.find("default").findall("param")
    channel = {}
    for cParam in params:
        key = cParam.get('name')
        val = cParam.get('value')
        channel[key] = val

    return channel

def getAllKeystores(appName):

    fileName = "games/" + appName + "/keystore.xml"

    configFile = file_utils.getFullPath(fileName)

    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except Exception as e:
        log_utils.error("can not parse keystore.xml.path:%s", configFile)
        return None

    channels = root.find("keystores").findall("channel")
    lstKeystores = []

    for cNode in channels:
        channel = {}
        params = cNode.findall("param")
        for cParam in params:
            key = cParam.get('name')
            val = cParam.get('value')
            channel[key] = val

        lstKeystores.append(channel)

    return lstKeystores


def getAppID():
    configFile = file_utils.getFullPath("config/config.xml")

    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except Exception as e:
        log_utils.error("can not parse config.xml.path:%s", configFile)
        return None

    gameNode = root.find("game")
    if gameNode == None:
        return None

    appID = gameNode.get('appID')

    return appID

def getAppKey():
    configFile = file_utils.getFullPath("config/config.xml")

    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except Exception as e:
        log_utils.error("can not parse config.xml.path:%s", configFile)
        return None

    gameNode = root.find("game")
    if gameNode == None:
        return None

    appID = gameNode.get('appKey')

    return appID


def getAllChannels(appName, isPublic):
    #读取games/游戏/config.xml里的信息
    fileName = "games/" + appName + "/config.xml"

    configFile = file_utils.getFullPath(fileName)

    if not os.path.exists(configFile):
        log_utils.error("%s is not exists", configFile)
        return

    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except Exception as e:
        log_utils.error("can not parse config.xml.path:%s",configFile)
        return None

    lstGPlugins = []
    globalPluginsNode = root.find("global-plugins")
    if globalPluginsNode is not None:
        globalPlugins = globalPluginsNode.findall("plugin")
        if globalPlugins is not None and len(globalPlugins) > 0:
            for pluginNode in globalPlugins:
                plugin = {}
                plugin['name'] = pluginNode.get("name")
                plugin['desc'] = pluginNode.get("desc")
                lstGPlugins.append(plugin)

    channels = root.find("channels").findall("channel")
    lstChannels = []
    for cNode in channels:
        channel = {}
        params = cNode.findall("param")
        for cParam in params:
            key = cParam.get('name')
            val = cParam.get('value')
            channel[key] = val


        sdkVersionNode = cNode.find('sdk-version')
        if sdkVersionNode != None and len(sdkVersionNode) > 0:
            versionCodeNode = sdkVersionNode.find('versionCode')
            versionNameNode = sdkVersionNode.find('versionName')
            if versionCodeNode != None and versionNameNode != None:
                # u8server use the logic version code to decide which sdk version to use
                channel['sdkLogicVersionCode'] = versionCodeNode.text
                channel['sdkLogicVersionName'] = versionNameNode.text


        sdkParams = cNode.find("sdk-params")
        tblSDKParams = {}

        if sdkParams != None:
            sdkParamNodes = sdkParams.findall('param')
            if sdkParamNodes != None and len(sdkParamNodes) > 0:
                for cParam in sdkParamNodes:
                    key = cParam.get('name')
                    val = cParam.get('value')
                    tblSDKParams[key] = val

        channel['sdkParams'] = tblSDKParams

        if len(lstGPlugins) > 0:
            for p in lstGPlugins:
                loadThirdPluginUserConfig(appName, channel, p, p['name'])


        ret = loadChannelUserConfig(appName, channel)
        if ret:
            lstPlugins = [] + lstGPlugins
            pluginsNode = cNode.find("plugins")

            if pluginsNode != None:
                pluginNodeLst = pluginsNode.findall("plugin")
                if pluginNodeLst != None and len(pluginNodeLst) > 0:

                    for cPlugin in pluginNodeLst:
                        plugin = {}
                        plugin['name'] = cPlugin.get('name')

                        exists = False
                        for p in lstPlugins:
                            if p['name'] == plugin['name']:
                                exists = True
                                break

                        if not exists:
                            plugin['desc'] = cPlugin.get('desc')
                            loadThirdPluginUserConfig(appName, channel, plugin, plugin['name'])
                            lstPlugins.append(plugin)

            channel['third-plugins'] = lstPlugins
            lstChannels.append(channel)

    return lstChannels

def loadThirdPluginUserConfig(appName, channel, plugin, pluginName):
    #configFile = file_utils.getFullPath("config/plugin/" + pluginName + "/config.xml")
    configFile = file_utils.getFullPath("games/" + appName + "/channels/" + channel['id'] + "/plugin/" + pluginName + "/config.xml")

    if not os.path.exists(configFile):
        configFile = file_utils.getFullPath("games/"+appName+"/plugin/"+pluginName+"/config.xml")
        if not os.path.exists(configFile):
            log_utils.error("the plugin %s config.xml file is not exists.path:%s", pluginName, configFile)
            return 0

    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except:
        log_utils.error("can not parse config.xml.path:%s", configFile)
        return 0

    configNode = root

    subpluginNodes = configNode.find("subplugins")

    if subpluginNodes != None and len(subpluginNodes) > 0:
        plugin['subplugins'] = []
        for subNode in subpluginNodes:
            subplugin = {}
            subplugin['name'] = subNode.get('name')
            subplugin['desc'] = subNode.get('desc')
            subParamNodes = subNode.findall('param')
            subplugin['params'] = []
            if subParamNodes != None and len(subParamNodes) > 0:
                for subParamNode in subParamNodes:
                    param = {}
                    param['name'] = subParamNode.get('name')
                    param['value'] = subParamNode.get('value')
                    param['required'] = subParamNode.get('required')
                    param['showName'] = subParamNode.get('showName')
                    param['bWriteInManifest'] = subParamNode.get('bWriteInManifest')
                    param['bWriteInClient'] = subParamNode.get('bWriteInClient')
                    subplugin['params'].append(param)

            plugin['subplugins'].append(subplugin)


    paramNodes = configNode.find("params")
    plugin['params'] = []
    if paramNodes != None and len(paramNodes) > 0:

        for paramNode in paramNodes:
            param = {}
            param['name'] = paramNode.get('name')
            param['value'] = paramNode.get('value')
            param['required'] = paramNode.get('required')
            param['showName'] = paramNode.get('showName')
            param['bWriteInManifest'] = paramNode.get('bWriteInManifest')
            param['bWriteInClient'] = paramNode.get('bWriteInClient')
            plugin['params'].append(param)

    operationNodes = configNode.find("operations")
    plugin['operations'] = []
    if operationNodes != None and len(operationNodes) > 0:

        for opNode in operationNodes:
            op = {}
            op['type'] = opNode.get('type')
            op['from'] = opNode.get('from')
            op['to'] = opNode.get('to')
            plugin['operations'].append(op)

    pluginNodes = configNode.find("plugins")
    if pluginNodes != None and len(pluginNodes) > 0:
        plugin['plugins'] = []
        for pNode in pluginNodes:
            p = {}
            p['name'] = pNode.get('name')
            p['type'] = pNode.get('type')
            plugin['plugins'].append(p)

    return 1

def loadChannelUserConfig(appName, channel):
    #读取config/sdk/渠道/config.xml里的信息
    configFile = file_utils.getFullPath("config/sdk/" + channel['sdk'] + "/config.xml")

    if not os.path.exists(configFile):
        log_utils.error("the config.xml is not exists of sdk %s.path:%s", channel['name'], configFile)
        return 0

    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
    except:
        log_utils.error("can not parse config.xml.path:%s", configFile)
        return 0

    configNode = root

    paramNodes = configNode.find("params")
    channel['params'] = []
    if paramNodes != None and len(paramNodes) > 0:

        for paramNode in paramNodes:
            param = {}
            param['name'] = paramNode.get('name')
            param['required'] = paramNode.get('required')

            if param['required'] == '1':

                key = param['name']
                if key in channel['sdkParams'] and channel['sdkParams'][key] != None:
                    param['value'] = channel['sdkParams'][key]
                else:
                    log_utils.error("the sdk %s 'sdkParam's is not all configed in the config.xml.path:%s", channel['name'], configFile)
                    return 0
            else:
                param['value'] = paramNode.get('value')

            param['showName'] = paramNode.get('showName')
            param['bWriteInManifest'] = paramNode.get('bWriteInManifest')
            param['bWriteInClient'] = paramNode.get('bWriteInClient')
            channel['params'].append(param)

    operationNodes = configNode.find("operations")
    channel['operations'] = []
    if operationNodes != None and len(operationNodes) > 0:

        for opNode in operationNodes:
            op = {}
            op['type'] = opNode.get('type')
            op['from'] = opNode.get('from')
            op['to'] = opNode.get('to')
            channel['operations'].append(op)

    pluginNodes = configNode.find("plugins")
    if pluginNodes != None and len(pluginNodes) > 0:
        channel['plugins'] = []
        for pNode in pluginNodes:
            p = {}
            p['name'] = pNode.get('name')
            p['type'] = pNode.get('type')
            channel['plugins'].append(p)

    #卢-->判断config。xml中是否有dependencies标签，并拼接到channel中
    dependencyNodes = configNode.find("dependencies")
    if dependencyNodes != None and len(dependencyNodes) > 0:
        channel['dependencies'] = []
        for depenNode in dependencyNodes:
            depen = {}
            depen['name'] = depenNode.get('name')
            if('group' in depenNode.keys()):
                depen['group'] = depenNode.get('group')
            if('module' in depenNode.keys()):
                depen['module'] = depenNode.get('module')
            if('processor' in depenNode.keys()):
                depen['processor'] = depenNode.get('processor')             
            channel['dependencies'].append(depen)
            
    return 1

def writeDeveloperProperties(game, channel, targetFilePath):

    targetFilePath = file_utils.getFullPath(targetFilePath)

    proStr = ""
    if channel['params'] != None and len(channel['params']) > 0:
        for param in channel['params']:
            if param['bWriteInClient'] == '1':
                proStr = proStr + param['name'] + "=" + param['value'] + "\n"

    if "sdkLogicVersionName" in channel:
        proStr = proStr + "U8_SDK_VERSION_NAME=" + channel["sdkLogicVersionName"] + "\n"

    proStr = proStr + "U8_Channel=" + channel['id'] + "\n"
    proStr = proStr + "U8_APPID=" + game["appID"] + "\n"
    proStr = proStr + "U8_APPKEY=" + game["appKey"] + "\n"

    showSplash = "false"
    if "splash" in channel and int(channel["splash"]) > 0 :
        showSplash = "true"

    proStr = proStr + "U8_SDK_SHOW_SPLASH=" + showSplash + "\n"

    useU8Auth = None
    authUrl = None

    #优先获取games/games.xml里数据
    if "use_u8_auth" in game:
        useU8Auth = game["use_u8_auth"]

    if "u8_auth_url" in game:
        authUrl = game["u8_auth_url"]


    #append u8 local config
    local_config = getLocalConfig()

    if useU8Auth is None or authUrl is None:
        if "use_u8_auth" not in local_config or "u8_auth_url" not in local_config:
            log_utils.error("the use_u8_auth or u8_auth_url is not exists in local.properties. don't use u8 auth.")
            return

        if local_config['use_u8_auth'] == "1":
            useU8Auth = "1"
            authUrl = local_config['u8_auth_url']


    if useU8Auth == "1":
        proStr = proStr + "U8_AUTH_URL=" + authUrl + "\n"

    # if "u8_analytics_url" in local_config:
    #     proStr = proStr + "U8_ANALYTICS_URL=" + local_config['u8_analytics_url'] + "\n"

    # if "u8_login_game_url" in local_config:
    #     proStr = proStr + "U8_LOGIN_GAME_URL=" + local_config['u8_login_game_url'] + "\n"

    # if "u8_order_url" in local_config:
    #     proStr = proStr + "U8_ORDER_URL=" + local_config['u8_order_url'] + "\n"

    # if "u8_posid_url" in local_config:
    #     proStr = proStr + "U8_POSID_URL=" + local_config['u8_posid_url'] + "\n"

    # if "sdk_update_url" in local_config:
    #     proStr = proStr + "SDK_UPDATE_URL=" + local_config['sdk_update_url'] + "\n"


    #write third plugin info:
    plugins = channel.get('third-plugins')
    if plugins != None and len(plugins) > 0:

        for plugin in plugins:
            if 'params' in plugin and plugin['params'] != None and len(plugin['params']) > 0:
                for param in plugin['params']:
                    if param['bWriteInClient'] == '1':
                        proStr = proStr + param['name'] + "=" + param['value'] + "\n"

    log_utils.debug("the develop info is %s", proStr)
    targetFile = open(targetFilePath, 'wb')
    proStr = proStr.encode('UTF-8')
    targetFile.write(proStr)
    targetFile.close()


def writePluginConfigs(channel, targetFilePath):
    targetTree = None
    targetRoot = None
    pluginNodes = None

    targetTree = ElementTree()
    targetRoot = Element('plugins')
    targetTree._setroot(targetRoot)

    if 'plugins' in channel:
        for plugin in channel['plugins']:
            typeTag = 'plugin'
            typeName = plugin['name']
            typeVal = plugin['type']
            pluginNode = SubElement(targetRoot, typeTag)
            pluginNode.set('name', typeName)
            pluginNode.set('type', typeVal)

    # write third plugin info
    thirdPlugins = channel.get('third-plugins')
    if thirdPlugins != None and len(thirdPlugins) > 0:
        for cPlugin in thirdPlugins:

            if 'plugins' in cPlugin and cPlugin['plugins'] != None and len(cPlugin['plugins']) > 0:
                for plugin in cPlugin['plugins']:
                    typeTag = 'plugin'
                    typeName = plugin['name']
                    typeVal = plugin['type']
                    pluginNode = SubElement(targetRoot, typeTag)
                    pluginNode.set('name', typeName)
                    pluginNode.set('type', typeVal)


    targetTree.write(targetFilePath, 'UTF-8')


#卢-->修改build.gradle
def writeGradleDependencies(dependencies, sdkDestDir):
    gradlePath = sdkDestDir + "/build.gradle"
    gradlePath = file_utils.getFullPath(gradlePath)

    gradleFile = open(gradlePath, 'r')
    lines = gradleFile.readlines()
    gradleFile.close()

    newLines = []
    for line in lines:
        newLines.append(line)                                         
        for depenNode in dependencies:   
            if 'dependencies' in line:

                if('name' in depenNode.keys()):
                    name = depenNode['name']
                    newLines.append("    compile ('" + name + "')\n")

                    if('group' in depenNode.keys() and 'module' not in depenNode.keys()):
                        group = depenNode['group']
                        if(group != None and len(group) > 0):
                            newLines.append("    {\n        exclude group:'" + group + "'\n    }\n")

                    if('group' in depenNode.keys() and 'module' in depenNode.keys()):
                        group = depenNode['group']
                        module = depenNode['module']
                        if((group != None and len(group) > 0) and (module != None and len(module) > 0)):
                            newLines.append("    {\n        exclude group:'" + group + "', module:'"+ module +"'\n    }\n")

                    if('group' not in depenNode.keys() and 'module' in depenNode.keys()):
                        module = depenNode['module']
                        if(module != None and len(module) > 0):
                            newLines.append("    {\n        exclude module:'"+ module +"'\n    }\n")
                    
                if('processor' in depenNode.keys()):
                    processor = depenNode['processor']
                    newLines.append("    annotationProcessor ('" + processor + "')\n")

                
   
    content = ''
    for line in newLines:
        content = content + line
    gradleFile = open(gradlePath, 'w')
    gradleFile.write(content)
    gradleFile.close()

    executeGradlew(sdkDestDir)

#卢-->下载依赖包到指定目录
def executeGradlew(sdkDestDir):
    libsDir = os.path.join(sdkDestDir, "libs")
    if not os.path.exists(libsDir):
        os.makedirs(libsDir)

    cmd = '''
    cd %s & \
    gradle copyToLibs & \
    ''' % (sdkDestDir)

    os.system(cmd)

