#include "db_manager.h"
#include "Token_verificator.h"
#include "ID_verificator.h"
#include "User_operations.h"
#include "ID_handler.h"
#include <iostream>

int main() {
    // 1. Initialize the database
    DBManager myDB("users.db");
    myDB.create_db();

    // 2. Initialize classes
    ID_verificator id_verifier(myDB);
    TokenVerificator token_verifier(myDB);
    User_operations user_ops(myDB); 
    
   //3. Initialize the request handler
   ID_handler handler(id_verifier, token_verifier, user_ops);
   
    return 0;
}