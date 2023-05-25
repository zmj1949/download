console.log(' 加载脚本');
setTimeout(main,0)

function hook_xindun() {
    
	var cls = Java.use('com.xindun.sdk.ApiNative')
	cls.processCmd.implementation = function(a, context, b){
				
		send(arguments);
		var retval = this.processCmd(a,context,b);
        //console.log("retval  ==> ", retval);
		send("retval  ==>"+retval);
        return retval;
	}


}

function main() {
    try {
        Java.perform(function () {
			send({"type": "isHook"})
            console.log(' 检测到安卓版本：' + Java.androidVersion);          
			hook_xindun();
		});	
    } catch (e) {
        console.log(e)
    }
}