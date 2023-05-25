console.log(' 加载脚本');
setTimeout(main,0)

function hook_xindun() {
    
	Java.use("com.xindun.sdk.ApiNative").processCmd.implementation = function (int,context,Object[]) {
				
		console.log("int,context,Object[]  ==> ", int,context,Object[]);

		var retval = this.processCmd(int,context,Object[]);
        console.log("retval  ==> ", retval);

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