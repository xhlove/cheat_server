# cheat_server

推荐使用另一种更灵活方便的方式

**https://blog.weimo.info/archives/598/**

## 关于

本脚本/软件是为方便调试网页中的js所写，需要配合Gooreplacer插件使用（或者其他一类重定向请求的插件）。

## 使用

- 将js文件放在config.json配置中`scripts_path`对应的相对目录中，默认`scripts`
- 在配置文件中配置你所需要的返回头
- 配置好你需要的端口和地址，默认地址`127.0.0.1`，默认端口`22222`
- 运行exe或脚本
- 在Gooreplacer插件中重定向网页中的js到`http://127.0.0.1:22222/js文件名`，并使规则生效

好了，现在你可以在本地实时修改js了，在浏览器中刷新就能生效了。
注意在Network一栏选中Disable Cache或者给本地的js配置中设定不缓存，~~但也需要强制刷新一遍才能生效~~。

## 其他

示例参考：https://blog.weimo.info/archives/441
