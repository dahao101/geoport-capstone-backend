from fastapi import HTTPException, status, BackgroundTasks
from fastapi import HTTPException, status


# main function
def bulk_message_main(recepient):
    try:

        message_sender(recepient)

    except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 



#message sender
def message_sender(recepient):
        print('sms sent to ',recepient)

bulk_message_main()
